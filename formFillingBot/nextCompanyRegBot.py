import logging
from pymongo import MongoClient
import requests
import azure.functions as func
import json
import openai
import re

# MongoDB Configuration
mongo_client = MongoClient("mongodb://<MONGO_DB_CONNECTION_STRING>")
db = mongo_client["ladki_bahin_yojna"]
users_collection = db["user_sessions"]

# In-Memory Session Storage
sessions = {}

# OpenAI API Key
openai.api_key = "YOUR_OPENAI_API_KEY"

### Workflow Steps ###
workflow_steps = [
    "eligibility_check", "basic_details", "bank_details",
    "educational_details", "family_income", "document_upload", "declaration"
]

mandatory_documents = [
    "Aadhaar Card", "Class 10 Certificate", "BPL Card", 
    "Bank Passbook/Cancelled Cheque", "Residential Proof"
]

# Workflow Prompts
prompts = {
    "eligibility_check": "Let’s check your eligibility:\n1. Are you a resident of Maharashtra? (Yes/No)\n2. Are you a girl child aged between 18 and 35 years? (Yes/No)\n3. Do you belong to a Below Poverty Line (BPL) family? (Yes/No)\n4. Have you completed education up to Class 10? (Yes/No)\n5. Are you unmarried or divorced? (Yes/No):",
    "basic_details": "Please provide your personal details:\n1. Full Name:\n2. Father's or Guardian's Name:\n3. Date of Birth (DD/MM/YYYY):\n4. Aadhaar Number:\n5. Mobile Number:\n6. Address (House Number/Street, Village/Town, District, PIN Code):",
    "bank_details": "Please provide your bank account details:\n1. Bank Name:\n2. Branch Name:\n3. Account Holder's Name:\n4. Account Number:\n5. IFSC Code:",
    "educational_details": "Provide your educational qualifications:\n1. Name of the School/Institution (last attended):\n2. Year of Passing Class 10:\n3. Marks Obtained in Class 10:\n4. Do you have a valid Class 10 certificate? (Yes/No):",
    "family_income": "Please provide your family's income details:\n1. Total Annual Family Income (in INR):\n2. Source(s) of Income (e.g., Agriculture, Daily Wage, etc.):\n3. Do you have a valid BPL card? (Yes/No):",
    "document_upload": f"Upload the following mandatory documents:\n{', '.join(mandatory_documents)}.\nPlease upload one document at a time.",
    "declaration": "Please confirm the following declaration:\n'I hereby declare that all the information provided is true to the best of my knowledge, and I understand that any false information may lead to the rejection of my application.'\nType 'YES' to agree and complete the process."
}


### Helper Functions ###
def get_user_session(user_id):
    """Fetch the user session."""
    if user_id not in sessions:
        sessions[user_id] = {"current_step": "eligibility_check", "data": {}, "documents": {}, "retry_count": 0}
    return sessions[user_id]

def save_user_data(user_id, key, value):
    """Save user data into MongoDB."""
    user_data = users_collection.find_one({"user_id": user_id})
    if not user_data:
        users_collection.insert_one({"user_id": user_id, "data": {key: value}, "documents": {}})
    else:
        user_data["data"][key] = value
        users_collection.update_one({"user_id": user_id}, {"$set": {"data": user_data["data"]}})

def save_document(user_id, doc_name, doc_url):
    """Save document upload details."""
    user_data = users_collection.find_one({"user_id": user_id})
    if not user_data:
        users_collection.insert_one({"user_id": user_id, "data": {}, "documents": {doc_name: doc_url}})
    else:
        documents = user_data.get("documents", {})
        documents[doc_name] = doc_url
        users_collection.update_one({"user_id": user_id}, {"$set": {"documents": documents}})

def move_to_next_step(session):
    """Advance the workflow step."""
    current_step = session["current_step"]
    next_step_index = workflow_steps.index(current_step) + 1
    if next_step_index < len(workflow_steps):
        session["current_step"] = workflow_steps[next_step_index]
    else:
        session["current_step"] = "completed"

def validate_step_data(current_step, user_input):
    """Validate the data provided by the user for the current step."""
    validation_rules = {
        "eligibility_check": {
            "questions": 5,
            "valid_responses": ["Yes", "No"]
        },
        "basic_details": {
            "fields": ["Full Name", "Date of Birth", "Aadhaar Number", "Mobile Number", "Address"],
            "patterns": {
                "Date of Birth": r"^\\d{2}/\\d{2}/\\d{4}$",  # DD/MM/YYYY
                "Aadhaar Number": r"^\\d{12}$",
                "Mobile Number": r"^\\d{10}$"
            }
        },
        "bank_details": {
            "fields": ["Bank Name", "Branch Name", "Account Holder's Name", "Account Number", "IFSC Code"],
            "patterns": {
                "Account Number": r"^\\d{9,18}$",
                "IFSC Code": r"^[A-Z]{4}0[A-Z0-9]{6}$"
            }
        },
        "educational_details": {
            "fields": ["Name of the School/Institution", "Year of Passing Class 10", "Marks Obtained in Class 10"],
            "patterns": {
                "Year of Passing Class 10": r"^\\d{4}$",
                "Marks Obtained in Class 10": r"^\\d{1,3}$"
            }
        },
        "family_income": {
            "fields": ["Total Annual Family Income", "Source(s) of Income"],
            "patterns": {
                "Total Annual Family Income": r"^\\d+(\\.\\d{1,2})?$"  # Valid number format
            }
        }
    }

    rules = validation_rules.get(current_step, {})
    missing_fields = []
    invalid_fields = []

    # Check for missing fields
    for field in rules.get("fields", []):
        if field not in user_input or not user_input[field]:
            missing_fields.append(field)

    # Validate patterns
    for field, pattern in rules.get("patterns", {}).items():
        if field in user_input and not re.match(pattern, user_input[field]):
            invalid_fields.append(field)

    if missing_fields or invalid_fields:
        return False, {
            "missing_fields": missing_fields,
            "invalid_fields": invalid_fields
        }
    return True, "Valid input."

def list_missing_documents(user_id):
    """Check and return missing documents."""
    user_data = users_collection.find_one({"user_id": user_id})
    uploaded_documents = user_data.get("documents", {})
    missing_mandatory = [doc for doc in mandatory_documents if doc not in uploaded_documents]
    return missing_mandatory

def generate_response(prompt, user_input):
    """Generate a response using OpenAI."""
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"{prompt}\nUser Input: {user_input}\nResponse:",
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return "I'm sorry, I couldn't process your response. Please try again."

def send_message_via_whatsapp(recipient_id, message):
    """Send a message using WhatsApp Business API."""
    url = "https://graph.facebook.com/v15.0/your-whatsapp-business-id/messages"
    headers = {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message},
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        logging.error(f"Failed to send message: {response.json()}")
    return response.json()

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Handle incoming WhatsApp messages."""
    logging.info('Python HTTP trigger function processed a request.')

    try:
        data = req.get_json()

        # Parse data received from WhatsApp API
        messages = data.get("entry", [])[0].get("changes", [])[0].get("value", {}).get("messages", [])
        if not messages:
            return func.HttpResponse(body=json.dumps({"status": "no_messages"}), mimetype="application/json")

        # Get message details
        message = messages[0]
        user_id = message["from"]
        session = get_user_session(user_id)
        current_step = session["current_step"]

        # Handle document uploads
        if message.get("type") == "document":
            document_url = message["document"]["link"]
            document_name = message["document"]["filename"]
            save_document(user_id, document_name, document_url)
            send_message_via_whatsapp(user_id, f"Received your document: {document_name}.")
            return func.HttpResponse(body=json.dumps({"status": "document_received"}), mimetype="application/json")

        # Handle text messages
        user_input = message["text"]["body"]
        prompt = prompts.get(current_step, "Thank you! Workflow is completed.")
        is_valid, validation_result = validate_step_data(current_step, user_input)

        if not is_valid:
            missing = validation_result.get("missing_fields", [])
            invalid = validation_result.get("invalid_fields", [])
            response_message = ""

            if missing:
                response_message += f"Missing fields: {', '.join(missing)}. "
            if invalid:
                response_message += f"Invalid fields: {', '.join(invalid)}. "
            response_message += "Please correct and resend."

            send_message_via_whatsapp(user_id, response_message)
            return func.HttpResponse(body=json.dumps({"status": "incomplete_data"}), mimetype="application/json")

        save_user_data(user_id, current_step, user_input)
        move_to_next_step(session)

        if session["current_step"] == "completed":
            missing_docs = list_missing_documents(user_id)
            if missing_docs:
                send_message_via_whatsapp(user_id, f"Missing mandatory documents: {', '.join(missing_docs)}. Please upload them.")
            else:
                send_message_via_whatsapp(user_id, "All details and documents have been collected. Thank you!")
            return func.HttpResponse(body=json.dumps({"status": "completed"}), mimetype="application/json")

        next_prompt = prompts.get(session["current_step"], "Thank you! Workflow is completed.")
        send_message_via_whatsapp(user_id, next_prompt)

        return func.HttpResponse(body=json.dumps({"status": "success"}), mimetype="application/json")

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(body=json.dumps({"status": "error", "message": str(e)}), mimetype="application/json", status_code=500)
