import logging
from pymongo import MongoClient
import requests
import azure.functions as func
import json
import openai
import re

WHATSAPP_TOKEN = ""
WA_URL = "https://graph.facebook.com/v15.0/your-whatsapp-business-id/messages"
openai.api_key = "YOUR_OPENAI_API_KEY"

mongo_client = MongoClient("mongodb://<MONGO_DB_CONNECTION_STRING>")
db = mongo_client["ladki_bahin_yojna"]
users_collection = db["user_sessions"]



# In-Memory Session Storage
sessions = {}

# OpenAI API Key

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
        sessions[user_id] = {"current_step": "eligibility_check", "data": {}, "documents": {}, "pending_fields": [], "retry_count": 0}
    return sessions[user_id]

def save_user_data(user_id, fields):
    """Save user data into MongoDB."""
    user_data = users_collection.find_one({"user_id": user_id})
    if not user_data:
        users_collection.insert_one({"user_id": user_id, "data": fields, "documents": {}})
    else:
        user_data["data"].update(fields)
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
        session["pending_fields"] = []  # Reset pending fields for the new step
    else:
        session["current_step"] = "completed"

def extract_fields_with_openai(prompt, user_input):
    """Use OpenAI to extract fields from user input."""
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Extract the following fields from the user input:\n{prompt}\nUser Input: {user_input}\nExtracted Fields:",
            max_tokens=150
        )
        fields = json.loads(response.choices[0].text.strip())
        return fields
    except Exception as e:
        logging.error(f"Error extracting fields with OpenAI: {e}")
        return {}

def validate_and_update_session(session, extracted_fields, validation_rules):
    """Validate extracted fields and update session data."""
    missing_fields = []
    invalid_fields = []

    for field in validation_rules.get("fields", []):
        if field not in extracted_fields or not extracted_fields[field]:
            missing_fields.append(field)

    for field, pattern in validation_rules.get("patterns", {}).items():
        if field in extracted_fields and not re.match(pattern, extracted_fields[field]):
            invalid_fields.append(field)

    session["data"].update({k: v for k, v in extracted_fields.items() if k not in invalid_fields})
    session["pending_fields"] = missing_fields + invalid_fields

    if session["pending_fields"]:
        return False
    return True

def send_message_via_whatsapp(recipient_id, message):
    """Send a message using WhatsApp Business API."""
    url = WA_URL
    headers = {
        "Authorization": WHATSAPP_TOKEN,
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
        validation_rules = prompts.get(current_step, {})

        # Handle document uploads
        if message.get("type") == "document":
            document_url = message["document"]["link"]
            document_name = message["document"]["filename"]
            save_document(user_id, document_name, document_url)
            send_message_via_whatsapp(user_id, f"Received your document: {document_name}.")
            return func.HttpResponse(body=json.dumps({"status": "document_received"}), mimetype="application/json")

        # Handle text messages
        user_input = message["text"]["body"]
        extracted_fields = extract_fields_with_openai(prompts[current_step], user_input)

        # Validate and update session
        is_step_complete = validate_and_update_session(session, extracted_fields, validation_rules)

        if not is_step_complete:
            pending_fields = session["pending_fields"]
            send_message_via_whatsapp(user_id, f"Some details are missing or invalid: {', '.join(pending_fields)}. Please provide them.")
            return func.HttpResponse(body=json.dumps({"status": "step_incomplete"}), mimetype="application/json")

        # Save valid data
        save_user_data(user_id, extracted_fields)

        # Move to the next step
        move_to_next_step(session)

        # Handle completion
        if session["current_step"] == "completed":
            send_message_via_whatsapp(user_id, "All details and documents have been collected. Thank you!")
            return func.HttpResponse(body=json.dumps({"status": "completed"}), mimetype="application/json")

        # Send next step prompt
        next_prompt = prompts.get(session["current_step"], "Thank you! Workflow is completed.")
        send_message_via_whatsapp(user_id, next_prompt)

        return func.HttpResponse(body=json.dumps({"status": "success"}), mimetype="application/json")

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(body=json.dumps({"status": "error", "message": str(e)}), mimetype="application/json", status_code=500)
