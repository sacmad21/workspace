import os
import logging
import traceback
import requests
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import re
import json

from whatsAppTokens import tokens


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
AZURE_STORAGE_CONNECTION_KEY = os.getenv("AZURE_STORAGE_CONNECTION_KEY")


                                    
# WhatsApp API Configuration
wa_vars = tokens["BuilderBot"]

WHATSAPP_API_BASE_URL = os.getenv("WHATSAPP_API_BASE_URL")
WHATSAPP_CLOUD_API_PHONE_NUMBER_ID = wa_vars["WA_Phone_Number_ID"]
WHATSAPP_TOKEN = wa_vars["WA_Token"]

# ===========================
# 🔹 WhatsApp Messaging Utils
# ===========================

def send_whatsapp_message(phone_number, message):
    """
    Sends a WhatsApp message to a user.
    """
    try:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {"body": message},
        }
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }

        WA_URL = f"{WHATSAPP_API_BASE_URL}/{WHATSAPP_CLOUD_API_PHONE_NUMBER_ID}/messages"

        logging.info(WA_URL)
        logging.info(WHATSAPP_TOKEN)

        response = requests.post(WA_URL, json=payload, headers=headers)

        if response.status_code == 200:
            logging.info(f"✅ WhatsApp message sent to {phone_number}: {message}")
        else:
            logging.error(f"❌ Failed to send WhatsApp message to {phone_number}. Status: {response.status_code}, Response: {response.text}")

    except Exception as e:
        logging.error(f"❌ Exception in send_whatsapp_message: {str(e)}")
        logging.error(traceback.format_exc())



# ===========================
# 🔹 Function: Validate Parameters with Regex
# ===========================

def validate_parameters(params, state_config):
    """
    Validates extracted parameters against the regex patterns defined in state_config.json.

    Parameters:
    - params (dict): Extracted user parameters (e.g., income, PAN number, Aadhaar number).
    - state_name (str): The state for which validation is happening.

    Returns:
    - tuple: (valid_data, errors)
        - valid_data (dict): Contains valid parameters after successful validation.
        - errors (dict): Contains error messages for invalid parameters.
    """
    try:
        valid_data = {}
        errors = {}

        for param, value in params.items():
            param_config = state_config.get(param)

            if not param_config:
                logging.warning(f"⚠️ Parameter '{param}' is not defined in state config, skipping validation.")
                valid_data[param] = value
                continue

            is_required = param_config.get("required", False)
            validation = param_config.get("validation", {})

            # If parameter is required but missing
            if is_required and not value:
                errors[param] = f"❌ '{param}' is required but missing."
                logging.error(errors[param])
                continue

            # Validate against regex if available
            regex_pattern = validation.get("regex")
            error_message = validation.get("error_message", f"❌ Invalid format for '{param}'.")

            if regex_pattern:
                try:
                    if not re.match(regex_pattern, str(value)):
                        errors[param] = error_message
                        logging.error(f"❌ Validation failed for '{param}': {value} | Expected Format: {regex_pattern}")
                        continue
                except re.error as regex_error:
                    logging.error(f"⚠️ Invalid regex pattern for '{param}': {regex_pattern} | Error: {regex_error}")
                    errors[param] = f"❌ Regex error in validation rule for '{param}'."
                    continue

            # If all checks pass, add to valid_data
            valid_data[param] = value
            logging.info(f"✅ '{param}' validated successfully: {value}")


        if errors:
            logging.warning(f"⚠️ Validation errors found: {errors}")

        return valid_data, errors

    except Exception as e:
        logging.error(f"❌ Exception in validate_parameters: {str(e)}")
        logging.error(traceback.format_exc())
        return {}, {}


# ===========================
# 🔹 Azure Blob Storage Utils
# ===========================
def upload_document_to_blob(document):
    """
    Uploads the document to Azure Blob Storage and returns the file URL.
    """
    try:
        blob_service = BlobServiceClient.from_connection_string(account_url=AZURE_STORAGE_CONNECTION, credential=AZURE_STORAGE_CONNECTION_KEY)
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
