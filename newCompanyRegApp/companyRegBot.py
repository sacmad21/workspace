import logging
from pymongo import MongoClient
import requests
import azure.functions as func
import json
from openai import OpenAI 
import openai
import traceback 

#WHATSAPP_TOKEN="EAARfYvT6wOgBO9qvOuzjTn5khoM2XZBfmQUqRvnMa2W1bXtDBZC8Tz03xTB1MQZABAhGZAllMx4xyIO2McBwu0nVRYQcECLDAHBDjNf2cSAaCTLthKSe2QiRGiCpqaBZBX1X50z660kHXlntsEwN8YJetR2ofGBnpdT7wX6l4OZC6EJmfFjoWsiXgEjbDBZC0xmxyTGpfJzbNlN7pMdCZBeepNMd5ZA4JczAYqwBphZCOQ"

#WHATSAPP_TOKEN="Bearer EAARfYvT6wOgBOZBU7KmaAGZCaHbsaYvYwmkRNNBJaz6VzFxF2zqZBSWfDhFfgokXdJGdkZA2NV7977RvfCW1lqp57jvAu8yxiNMznej4ot53w2H9n0KxQAZAUKzpNWP2sN9Opd7ZBztVRwe4jVoxCw1kiKNu8a3c9jsrDzqAualtctLnwAPAv3Gvedy4xZA7HUEySYRwATD6pwCpkPy2ezNBUZCkNWDp"
WHATSAPP_TOKEN="Bearer EAARfYvT6wOgBO9qvOuzjTn5khoM2XZBfmQUqRvnMa2W1bXtDBZC8Tz03xTB1MQZABAhGZAllMx4xyIO2McBwu0nVRYQcECLDAHBDjNf2cSAaCTLthKSe2QiRGiCpqaBZBX1X50z660kHXlntsEwN8YJetR2ofGBnpdT7wX6l4OZC6EJmfFjoWsiXgEjbDBZC0xmxyTGpfJzbNlN7pMdCZBeepNMd5ZA4JczAYqwBphZCOQ"

WHATSAPP_API_BASE_URL="https://graph.facebook.com/v15.0"
WHATSAPP_CLOUD_API_PHONE_NUMBER_ID="441143062411889"
GRAPH_API_TOKEN = "EAARfYvT6wOgBO9qvOuzjTn5khoM2XZBfmQUqRvnMa2W1bXtDBZC8Tz03xTB1MQZABAhGZAllMx4xyIO2McBwu0nVRYQcECLDAHBDjNf2cSAaCTLthKSe2QiRGiCpqaBZBX1X50z660kHXlntsEwN8YJetR2ofGBnpdT7wX6l4OZC6EJmfFjoWsiXgEjbDBZC0xmxyTGpfJzbNlN7pMdCZBeepNMd5ZA4JczAYqwBphZCOQ"
WEBHOOK_VERIFY_TOKEN = "BINGO"


# mongodb://allbotdb:HJKQTAmnWGVoK8cAzwAto4zow3hXS02pDN3v37iOjhLHmGCdNAo86GEKOETpwD6IR4rqoVTU99mhACDbqHeJfg==@allbotdb.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&maxIdleTimeMS=120000&appName=@allbotdb@

# MongoDB Configuration
mongo_client = MongoClient("mongodb://allbotdb:HJKQTAmnWGVoK8cAzwAto4zow3hXS02pDN3v37iOjhLHmGCdNAo86GEKOETpwD6IR4rqoVTU99mhACDbqHeJfg==@allbotdb.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&maxIdleTimeMS=120000&appName=@allbotdb@")
db = mongo_client["govforms"]
users_collection = db["user_sessions"]


# In-Memory Session Storage
sessions = {}
user_responses = [] 

# OpenAI API Key
openai_api_key = "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"


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
    print("Get use Session ::", user_id)

    if user_id not in sessions:
        sessions[user_id] = {"current_step": "eligibility_check", "data": {}, "documents": {}, "retry_count": 0}
    return sessions[user_id]

def save_user_data(user_id, key, value):
    """Save user data into MongoDB."""

    print("Save user data ::", user_id, key, value)

    user_data = users_collection.find_one({"user_id": user_id})
    if not user_data:
        users_collection.insert_one({"user_id": user_id, "data": {key: value}, "documents": {}})
    else:
        user_data["data"][key] = value
        users_collection.update_one({"user_id": user_id}, {"$set": {"data": user_data["data"]}})

def save_document(user_id, doc_name, doc_url):
    """Save document upload details."""

    print("Save document ::", user_id, doc_name, doc_url)

    user_data = users_collection.find_one({"user_id": user_id})
    if not user_data:
        users_collection.insert_one({"user_id": user_id, "data": {}, "documents": {doc_name: doc_url}})
    else:
        documents = user_data.get("documents", {})
        documents[doc_name] = doc_url
        users_collection.update_one({"user_id": user_id}, {"$set": {"documents": documents}})

def move_to_next_step(session):
    """Advance the workflow step."""

    print("Move to next step ::", session["current_step"])

    current_step = session["current_step"]
    next_step_index = workflow_steps.index(current_step) + 1
    if next_step_index < len(workflow_steps):
        session["current_step"] = workflow_steps[next_step_index]
    else:
        session["current_step"] = "completed"

def list_missing_documents(user_id):
    """Check and return missing documents."""
    user_data = users_collection.find_one({"user_id": user_id})
    uploaded_documents = user_data.get("documents", {})
    missing_mandatory = [doc for doc in mandatory_documents if doc not in uploaded_documents]
    return missing_mandatory


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




def generate_response(form_section, user_input):
    """Generate a response using OpenAI."""

    print("Generate Response ::", form_section, user_input)

    name = "Sachin Khaire"

    final_promt = f"""
        Ask questions to User one by one from FORM_SECTION_PROMT. 
        Kindly improvise the questions if required to be more suitable based on the his/her responses.
        Don't repeat the question if answer is already available in user responses. 
        Once all the answers for all the questions are available in USER_RESPONSES then confirm all the answers with user.
        After user's confirmation generate JSON for all the available answers.

        FORM_SECTION_PROMT :::
        {form_section}

        NAME :::
        {name}

        CURRENT_RESPONSE :::
        {user_input}
        
        USER_RESPONSE :::
        {user_responses}

        """
    messages = []



    choices = None
    try:
        client = OpenAI(api_key=openai_api_key)
        print("\n\nFinal Prompt ::::\n", final_promt)

        response: any = client.chat.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=final_promt,
            max_tokens=1024
        )
        
        print ("Extraction response" , response)

        choices: any = response.choices[0]
        text = choices.text

        user_responses.append(user_input)

        is_step_complete = False
        extracted_fields = "NA"
        next_prompt = text.strip()

        print("Before Return : ", is_step_complete, extracted_fields, next_prompt )

        return is_step_complete,next_prompt,extracted_fields
    
    except Exception as e:
        traceback.print_exc() 
        logging.error(f"Error generating response: generate_response {e}")
        return "I'm sorry, I couldn't process your response. Please try again."


def extract_fields_with_openai(fields, user_input):
    """Use OpenAI to extract fields from user input."""
    client = OpenAI(api_key=openai_api_key)

    choices = None
    try:
        response: any = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Extract the following fields from the user input in JSON format:\n Fields::\n {fields}\nUser Input::\n {user_input}\nExtracted Fields:",
            
            
            max_tokens=150
        )
        print ("Extraction response" , response)
        choices: any = response.choices[0]
        fields = json.loads(choices.text.strip())
        return fields
    except Exception as e:
        traceback.print_exc() 

        logging.error(f"Error extracting fields with OpenAI: {e}")
        return {}





def send_message_via_whatsapp(recipient_id, message):
    """Send a message using WhatsApp Business API."""

    print("send_message_via_whatsapp ::", recipient_id, message)

    url = "https://graph.facebook.com/v15.0/441143062411889/messages"
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






def post_webhook(req: func.HttpRequest) -> func.HttpResponse:
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

        is_section_complete, next_prompt, extracted_fields = generate_response(prompt, user_input)
        print("\nGenerate Response\nFIN==", is_section_complete, "\nNP==" ,next_prompt, "\nFLD==" , extracted_fields )

        if is_section_complete == False:
            send_message_via_whatsapp(user_id, next_prompt)
            return func.HttpResponse(body=json.dumps({"status": "success", "message":next_prompt}), mimetype="application/json")


        is_valid, validation_result = validate_step_data(current_step, extracted_fields)
        

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






# Function for handling GET requests (webhook verification)
def get_webhook(req: func.HttpRequest) -> func.HttpResponse:
    mode = req.params.get("hub.mode")
    token = req.params.get("hub.verify_token")
    challenge = req.params.get("hub.challenge")

    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        logging.info("Webhook verified successfully!")
        return func.HttpResponse(challenge, status_code=200)
    else:
        return func.HttpResponse("Forbidden", status_code=403)
