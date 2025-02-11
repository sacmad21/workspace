import os
import logging
import traceback
import requests
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Logger
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.DEBUG if os.getenv("DEBUG_MODE", "false").lower() == "true" else logging.INFO
)

# Azure Storage Configuration
AZURE_STORAGE_CONNECTION = os.getenv("AZURE_STORAGE_CONNECTION")
AZURE_BLOB_CONTAINER = os.getenv("AZURE_BLOB_CONTAINER")

# WhatsApp API Configuration
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")

# ===========================
# 🔹 WhatsApp Messaging Utils
# ===========================

def send_whatsapp_message(phone_number, message):
    """
    Sends a WhatsApp message to a user.
    """
    try:
        payload = {
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {"body": message},
        }
        headers = {
            "Authorization": f"Bearer {WHATSAPP_API_KEY}",
            "Content-Type": "application/json",
        }
        response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            logging.info(f"✅ WhatsApp message sent to {phone_number}: {message}")
        else:
            logging.error(f"❌ Failed to send WhatsApp message to {phone_number}. Status: {response.status_code}, Response: {response.text}")

    except Exception as e:
        logging.error(f"❌ Exception in send_whatsapp_message: {str(e)}")
        logging.error(traceback.format_exc())

# ===========================
# 🔹 Validation Functions
# ===========================

def is_number(value):
    """
    Checks if the value is a number.
    """
    try:
        float(value)
        return True
    except ValueError:
        logging.warning(f"⚠️ Validation failed: {value} is not a number.")
        return False

def is_employment_type(value):
    """
    Checks if employment type is 'Salaried' or 'Self-Employed'.
    """
    valid_types = ["salaried", "self-employed"]
    if value.lower() in valid_types:
        return True
    logging.warning(f"⚠️ Invalid employment type: {value}. Expected 'Salaried' or 'Self-Employed'.")
    return False

def validate_parameters(params, state_name):
    """
    Validates extracted parameters based on the state configuration.
    """
    from state_manager import STATE_CONFIG

    try:
        state_config = STATE_CONFIG.get(state_name, {}).get("parameters", {})
        valid_data = {}
        errors = {}

        for param, value in params.items():
            validation_rule = state_config.get(param, {}).get("validation")
            if validation_rule:
                validation_func = VALIDATION_FUNCTIONS.get(validation_rule)
                if validation_func and not validation_func(value):
                    errors[param] = state_config[param]["error_message"]
                else:
                    valid_data[param] = value

        if errors:
            logging.warning(f"⚠️ Parameter validation errors: {errors}")

        return valid_data, errors

    except Exception as e:
        logging.error(f"❌ Exception in validate_parameters: {str(e)}")
        logging.error(traceback.format_exc())
        return {}, {}

# Validation function mapping
VALIDATION_FUNCTIONS = {
    "is_number": is_number,
    "is_employment_type": is_employment_type,
}

# ===========================
# 🔹 Azure Blob Storage Utils
# ===========================

def upload_document_to_blob(document):
    """
    Uploads the document to Azure Blob Storage and returns the file URL.
    """
    try:
        blob_service = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION)
        container_client = blob_service.get_container_client(AZURE_BLOB_CONTAINER)

        blob_client = container_client.get_blob_client(document["filename"])
        blob_client.upload_blob(document["content"], overwrite=True)

        file_url = f"https://{AZURE_STORAGE_CONNECTION}.blob.core.windows.net/{AZURE_BLOB_CONTAINER}/{document['filename']}"
        logging.info(f"✅ Document uploaded successfully: {document['filename']}, URL: {file_url}")
        return file_url

    except Exception as e:
        logging.error(f"❌ Failed to upload document: {document['filename']}. Error: {str(e)}")
        logging.error(traceback.format_exc())
        return None

# ===========================
# 🔹 Generic Utility Functions
# ===========================

def format_response_message(data):
    """
    Formats a structured response message for WhatsApp.
    """
    try:
        message = "\n".join([f"✅ {key}: {value}" for key, value in data.items()])
        logging.debug(f"📄 Formatted response message: {message}")
        return message
    except Exception as e:
        logging.error(f"❌ Exception in format_response_message: {str(e)}")
        logging.error(traceback.format_exc())
        return "Error formatting response."

def extract_specific_field_from_text(text, field_name):
    """
    Extracts a specific field (like name, DOB) from the document text using GenAI.
    """
    from genAI import extract_text_from_document

    try:
        prompt = f"Extract the '{field_name}' from the following document text:\n{text}"
        extracted_value = extract_text_from_document(prompt)
        
        if extracted_value:
            logging.info(f"✅ Extracted '{field_name}': {extracted_value}")
            return extracted_value
        else:
            logging.warning(f"⚠️ Failed to extract '{field_name}' from document.")
            return None

    except Exception as e:
        logging.error(f"❌ Exception in extract_specific_field_from_text: {str(e)}")
        logging.error(traceback.format_exc())
        return None

def summarize_document(text):
    """
    Summarizes the extracted document text using GenAI.
    """
    from genAI import extract_text_from_document

    try:
        prompt = f"Summarize the following document:\n{text}"
        summary = extract_text_from_document(prompt)

        if summary:
            logging.info(f"📄 Document summary generated: {summary}")
            return summary
        else:
            logging.warning("⚠️ Document summarization failed.")
            return "Summary not available."

    except Exception as e:
        logging.error(f"❌ Exception in summarize_document: {str(e)}")
        logging.error(traceback.format_exc())
        return "Summary not available."
