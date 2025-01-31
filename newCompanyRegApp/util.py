import logging
from pymongo import MongoClient
import requests
import json
import openai
import re
import traceback
from azure.storage.filedatalake import DataLakeServiceClient


# WHATSAPP_TOKEN="EAARfYvT6wOgBO9qvOuzjTn5khoM2XZBfmQUqRvnMa2W1bXtDBZC8Tz03xTB1MQZABAhGZAllMx4xyIO2McBwu0nVRYQcECLDAHBDjNf2cSAaCTLthKSe2QiRGiCpqaBZBX1X50z660kHXlntsEwN8YJetR2ofGBnpdT7wX6l4OZC6EJmfFjoWsiXgEjbDBZC0xmxyTGpfJzbNlN7pMdCZBeepNMd5ZA4JczAYqwBphZCOQ"
# WHATSAPP_TOKEN="Bearer EAARfYvT6wOgBOZBU7KmaAGZCaHbsaYvYwmkRNNBJaz6VzFxF2zqZBSWfDhFfgokXdJGdkZA2NV7977RvfCW1lqp57jvAu8yxiNMznej4ot53w2H9n0KxQAZAUKzpNWP2sN9Opd7ZBztVRwe4jVoxCw1kiKNu8a3c9jsrDzqAualtctLnwAPAv3Gvedy4xZA7HUEySYRwATD6pwCpkPy2ezNBUZCkNWDp"
# WHATSAPP_TOKEN="Bearer EAARfYvT6wOgBO9qvOuzjTn5khoM2XZBfmQUqRvnMa2W1bXtDBZC8Tz03xTB1MQZABAhGZAllMx4xyIO2McBwu0nVRYQcECLDAHBDjNf2cSAaCTLthKSe2QiRGiCpqaBZBX1X50z660kHXlntsEwN8YJetR2ofGBnpdT7wX6l4OZC6EJmfFjoWsiXgEjbDBZC0xmxyTGpfJzbNlN7pMdCZBeepNMd5ZA4JczAYqwBphZCOQ"

WHATSAPP_TOKEN="Bearer EAARfYvT6wOgBO9qvOuzjTn5khoM2XZBfmQUqRvnMa2W1bXtDBZC8Tz03xTB1MQZABAhGZAllMx4xyIO2McBwu0nVRYQcECLDAHBDjNf2cSAaCTLthKSe2QiRGiCpqaBZBX1X50z660kHXlntsEwN8YJetR2ofGBnpdT7wX6l4OZC6EJmfFjoWsiXgEjbDBZC0xmxyTGpfJzbNlN7pMdCZBeepNMd5ZA4JczAYqwBphZCOQ"

WHATSAPP_API_BASE_URL="https://graph.facebook.com/v15.0/441143062411889"
GRAPH_API_TOKEN = "EAARfYvT6wOgBO9qvOuzjTn5khoM2XZBfmQUqRvnMa2W1bXtDBZC8Tz03xTB1MQZABAhGZAllMx4xyIO2McBwu0nVRYQcECLDAHBDjNf2cSAaCTLthKSe2QiRGiCpqaBZBX1X50z660kHXlntsEwN8YJetR2ofGBnpdT7wX6l4OZC6EJmfFjoWsiXgEjbDBZC0xmxyTGpfJzbNlN7pMdCZBeepNMd5ZA4JczAYqwBphZCOQ"
WEBHOOK_VERIFY_TOKEN = "BINGO"
openai_api_key = "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"
mongo_client = MongoClient("mongodb://allbotdb:HJKQTAmnWGVoK8cAzwAto4zow3hXS02pDN3v37iOjhLHmGCdNAo86GEKOETpwD6IR4rqoVTU99mhACDbqHeJfg==@allbotdb.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&maxIdleTimeMS=120000&appName=@allbotdb@")
db = mongo_client["govforms"]
users_collection = db["user_sessions"]
FIRST_STEP = "welcome"


#DATALAKE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=smklake;AccountKey=VkP1gNKzPSupXUF8P6LkFcYF61/uaPpUG8LY5m4ovuEyguV7AVS9bcaFBD321RNZh1ITTdO7butq+AStHx//uw==;EndpointSuffix=core.windows.net"
DATALAKE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=smklake;AccountKey=VkP1gNKzPSupXUF8P6LkFcYF61/uaPpUG8LY5m4ovuEyguV7AVS9bcaFBD321RNZh1ITTdO7butq+AStHx//uw==;EndpointSuffix=core.windows.net"
DATALAKE_KEY="VkP1gNKzPSupXUF8P6LkFcYF61/uaPpUG8LY5m4ovuEyguV7AVS9bcaFBD321RNZh1ITTdO7butq+AStHx//uw=="
FILE_SYSTEM_NAME="formfilling"
BLOB_BASE_DIR="ladkibahin"


# In-Memory Session Storage
sessions = {}


# Workflow Steps and Prompts (Can be moved to utility if reusable)
workflow_steps = ["welcome","eligibility_check", "basic_details", "bank_details", "educational_details", "family_income", "document_upload", "declaration"]

#workflow_steps = ["welcome","eligibility_check","declaration"]


mandatory_documents = [
    "Aadhaar Card", "Class 10 Certificate", "BPL Card", 
    "Bank Passbook/Cancelled Cheque", "Residential Proof"
]


# Workflow Prompts
prompts = {
    "welcome": "Welcome, Are you interested to apply for Ladki Bahin Yojana of Maharashtra Goverment ? (Yes/No)",
    "eligibility_check": "Let’s check your eligibility:\n1. Are you a resident of Maharashtra? (Yes/No)\n2. Are you a girl child aged between 18 and 35 years? (Yes/No)\n3. Do you belong to a Below Poverty Line (BPL) family? (Yes/No)\n4. Have you completed education up to Class 10? (Yes/No)\n5. Are you unmarried or divorced? (Yes/No):",
    "basic_details": "Please provide your personal details:\n1. What is your Full Name ?\n2. What is your Father's or Guardian's Name ?\n3. Date of Birth (DD-MM-YYYY) ?\n4. What is your Aadhaar Number ?\n5. What is your Mobile Number ?\n6. What is your Address (House Number/Street, Village/Town, District, PIN Code):",
    "bank_details": "Please provide your bank account details:\n1. What is account holder's name ?\n2. What is name of bank ?\n3. What is branch name ? \n4. What is account number:\n5. What is IFSC code ?",
    "educational_details": "Provide your educational qualifications:\n1. What is name of the School/Institution ? (last attended):\n2. What is the year of passing Class 10:\n3. How many Marks are obtained in Class 10 class?\n4. Do you have a valid passing certificate? (Yes/No):",
    "family_income": "Please provide your family's income details:\n1. What is Total Annual Family Income (in INR):\n2. What are Source(s) of Income ? (e.g., Agriculture, Daily Wage, etc.):\n3. Do you have a valid BPL card? (Yes/No):",
    "document_upload": f"Upload the following mandatory documents:\n{', '.join(mandatory_documents)}.\nPlease upload one document at a time.",
    "declaration": "Please confirm the following declaration:\n'I hereby declare that all the information provided is true to the best of my knowledge, and I understand that any false information may lead to the rejection of my application.'\nType 'YES' to agree and complete the process."
}

fields ={
    "welcome": ["isInterested"],
    "eligibility_check": ["isResident_of_Maharashtra", "isGirlChildBetween18and35Years", "isBPL","isEducationUptoClass10", "isUnmarriedOrDivorced"],
    "basic_details": ["fullName","fatherOrGuardianName","DOB","aadharNumber","mobileNumber","address"],
    "bank_details": ["bankName","branchName","accountHolderName","accountNumber","ifscCode"],
    "educational_details": ["nameOfInstution","yearOfPassingClass10","marksObtained","valid1Certificate"],
    "family_income": ["annualFamilyIncome","sourceOfIncome","doHaveBplCard"],
    "document_upload": ["isAdharCardUploaded","isClass10CertificateUploaded","isBPLCardUploaded","isCancelledChequeUploaded", "isResidentialProofUploaded"],
    "declaration": ["formDeclaration"],
}


validation_rules = {
    "welcome": {
        "questions": 1,
        "fields" : ["isInterested"],
        "valid_responses": ["Yes", "No"],
        "confirmation":True
    },

    "eligibility_check": {
        "questions": 5,
        "fields" : ["isResident_of_Maharashtra", "isGirlChildBetween18and35Years", "isBPL","isEducationUptoClass10", "isUnmarriedOrDivorced"],
        "valid_responses": ["Yes", "No"],
        "confirmation":True
    },

    "basic_details": {
        "fields": ["fullName","fatherOrGuardianName","DOB","aadharNumber","mobileNumber","address"],
        "patterns": {
            "DOB": r"^\d{2}-\d{2}-\d{4}$",  # DD/MM/YYYY
            "aadharNumber": r"^\d{12}$",
            "mobileNumber": r"^\d{10}$"
        },
        "confirmation":True

    },

    "bank_details": {
        "fields": ["bankName","branchName","accountHolderName","accountNumber","ifscCode"],
        "patterns": {
            "ifscCode": r"^[A-Z]{4}0[A-Z0-9]{6}$"
        },
        "confirmation":True

    },
    "educational_details": {
        "fields": ["nameOfInstution","yearOfPassingClass10","marksObtained","isValid1Certificate"],
        "patterns": {
            "yearOfPassingClass10": r"^\d{4}$",
            "marksOntainedIn10Class": r"^\d{1,3}$"
        },
        "confirmation":True

    },
    "family_income": {
        "fields": ["annualFamilyIncome","sourceOfIncome","doHaveBplCard"],
        "patterns": {
            "annualFamilyIncome": r"^\d+(\.\d{1,2})?$"  # Valid number format
        },
        "confirmation":True

    },

    "document_upload": {
        "fields": ["isAdharCardUploaded","isClass10CertificateUploaded","isBPLCardUploaded","isCancelledChequeUploaded", "isResidentialProofUploaded"],
        "confirmation":True
    }
}


def download_document_from_WA(media_url):
    """Download document file from the media URL."""
    headers = {
        "Authorization": WHATSAPP_TOKEN
    }
    response = requests.get(media_url, headers=headers)
    # print("WA File download Response", response)
    if response.status_code == 200:
        return response.content
    else:
        logging.error(f"Failed to download document: {response.status_code}, {response.text}")
        return None



def download_document_from_WA_pushto_ADL(media_url, user_id, document_name):
    """Download document file from the media URL and upload it to Azure Data Lake."""
    try:
        # Download the document from the media URL
        headers = {
            "Authorization": WHATSAPP_TOKEN
        }
        
        response = requests.get(media_url, headers=headers)

        # print("\nFile Download from WA :::::::::::::::::;\n",response)
        if response.status_code != 200:
            return None


        # Upload the document to Azure Data Lake
        service_client = DataLakeServiceClient.from_connection_string(DATALAKE_CONNECTION_STRING)
        
        file_system_client = service_client.get_file_system_client(FILE_SYSTEM_NAME)

        # Create a directory for the user if it doesn't exist
        directory_client = file_system_client.get_directory_client(f"{BLOB_BASE_DIR}/{user_id}/documents")
        try:
            directory_client.create_directory()
            print("\nDirectory created on Azure Lake:")
        except Exception as e:
            logging.info(f"Directory already exists: {e}")

        print("\nDocument NAME :::::::::::::::::::::::", document_name)
        print("\nContent       :::::::::::::::::::::::", document_content)
        # Upload the document
        file_client = directory_client.get_file_client(document_name)
        file_client.upload_data(document_content, overwrite=True)

        # Generate a URL for the uploaded document
        document_url = f"https://{service_client.account_name}.dfs.core.windows.net/{FILE_SYSTEM_NAME}/{BLOB_BASE_DIR}/{user_id}/documents/{document_name}"
        return document_url

    except Exception as e:
        traceback.print_exc() 
        logging.error(f"Error handling document upload to Azure Data Lake: {e}")
        return None




# Fetch Metadata of the media on WhatsApp 
def fetch_document_metadata(media_id):
    """Fetch document metadata using the WhatsApp Media API."""
    url = f"https://graph.facebook.com/v15.0/{media_id}"
    headers = {
        "Authorization": WHATSAPP_TOKEN
    }

    response = requests.get(url, headers=headers)
    print("\n\nMedia Metadata::", response)

    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch document metadata: {response.status_code}, {response.text}")
        return None



### Utility Functions ###
def get_user_session(user_id):
    """Fetch the user session."""
    if user_id not in sessions:
        sessions[user_id] = {"current_step": FIRST_STEP, "form": {}, "form_data":{}, "data": {}, "wa_message": "Welcome" , "documents": {}, "pending_fields": [], "retry_count": 0}
    return sessions[user_id]


def finalizeForm(user_id, session):
    
    
    sessions.pop(user_id)
    # Finalize the form 

    return True



def save_user_data(user_id, fields):
    """Save user data into MongoDB."""
    user_data = users_collection.find_one({"user_id": user_id})
    if not user_data:
        users_collection.insert_one({"user_id": user_id, "data": fields, "documents": {}})
    else:
        user_data["data"].update(fields)
        users_collection.update_one({"user_id": user_id}, {"$set": {"data": user_data["data"]}})



def save_document_from_url(user_id, doc_name, doc_url):
    """Save document upload details."""
    user_data = users_collection.find_one({"user_id": user_id})
    if not user_data:
        users_collection.insert_one({"user_id": user_id, "data": {}, "documents": {doc_name: doc_url}})
    else:
        documents = user_data.get("documents", {})
        documents[doc_name] = doc_url
        users_collection.update_one({"user_id": user_id}, {"$set": {"documents": documents}})



def doStepConfirmationRequired(session):
    """Advance the workflow step."""
    current_step = session["current_step"]

    if current_step in validation_rules.keys() :         
        return validation_rules[current_step]["confirmation"]
    
    return False 


def move_to_next_step(session):
    """Advance the workflow step."""
    current_step = session["current_step"]
    
    session["form"] |= session["data"]    
    session["form_data"][current_step] = session["data"]
    session["data"] = {} 
    
    next_step_index = workflow_steps.index(current_step) + 1

    if next_step_index < len(workflow_steps):
        session["current_step"] = workflow_steps[next_step_index]
        session["pending_fields"] = []  # Reset pending fields for the new step
    else:
        session["current_step"] = "completed"



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

    print("\nValidion:: Missed Fields :",  missing_fields)
    print("\nValidion:: Invalid Fields :", invalid_fields)
    
    if session["pending_fields"]:
        return False
    return True



def send_message_via_whatsapp(recipient_id, message):
    """Send a message using WhatsApp Business API."""
    url = WHATSAPP_API_BASE_URL +"/messages"
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

