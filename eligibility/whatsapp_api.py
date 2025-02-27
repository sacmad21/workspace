import requests
import json
import os
from dotenv import load_dotenv


load_dotenv()


WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_CLOUD_API_PHONE_NUMBER_ID")

WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"

HEADERS = {
    "Authorization": WHATSAPP_TOKEN ,
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
    
    response = requests.post(WHATSAPP_API_URL, headers=HEADERS, json=payload)
    return response.json()
