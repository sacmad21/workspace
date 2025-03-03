import requests
import json
import os
from dotenv import load_dotenv


load_dotenv()

from whatsAppTokens import tokens

# Load environment variables
load_dotenv()
# WhatsApp API Configuration

wa_vars = tokens["MpEligibilityCheckApp"]
print("\n\n ----------- Interactive :: ", os.getenv("WHATSAPP_INTERACTIVE_MESSAGE") )

WHATSAPP_API_BASE_URL = os.getenv("WHATSAPP_API_BASE_URL")
WHATSAPP_CLOUD_API_PHONE_NUMBER_ID = wa_vars["WA_Phone_Number_ID"]
WHATSAPP_TOKEN = wa_vars["WA_Token"]



#PHONE_NUMBER_ID = os.getenv("WHATSAPP_CLOUD_API_PHONE_NUMBER_ID")
#WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"



HEADERS = {
    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    "Content-Type": "application/json"
}

def send_whatsapp_message(phone_number, message):
    """
    Sends a WhatsApp message using WhatsApp Cloud API.
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "text": {"body": message}
    }
    url = f"{WHATSAPP_API_BASE_URL}/{WHATSAPP_CLOUD_API_PHONE_NUMBER_ID}/messages"

    print("Sending WhatsApp Message ::", payload)
    response = requests.post(url, headers=HEADERS, json=payload)
    print("WA Response", response)

    return response.json()


