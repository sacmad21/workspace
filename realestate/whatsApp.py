import requests
from fastapi import FastAPI, Request
from realestate.sceario_implementations import (
    handle_property_availability_query,
    send_greeting,
    get_suggested_search_options,
    handle_query_error,
    suggest_alternative_properties,
    handle_multilingual_query
)

app = FastAPI()

# WhatsApp Business API Credentials
WHATSAPP_API_URL = "https://graph.facebook.com/v15.0/441143062411889/messages"
ACCESS_TOKEN = "EAARfYvT6wOgBO9qvOuzjTn5khoM2XZBfmQUqRvnMa2W1bXtDBZC8Tz03xTB1MQZABAhGZAllMx4xyIO2McBwu0nVRYQcECLDAHBDjNf2cSAaCTLthKSe2QiRGiCpqaBZBX1X50z660kHXlntsEwN8YJetR2ofGBnpdT7wX6l4OZC6EJmfFjoWsiXgEjbDBZC0xmxyTGpfJzbNlN7pMdCZBeepNMd5ZA4JczAYqwBphZCOQ"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# GROQ API Credentials
GROQ_API_URL = "https://api.groq.com/v1/intent"
GROQ_API_KEY = "<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"

def get_intent_and_parameters_from_groq(message_text):
    """
    Use GROQ API to determine the intent and extract structured parameters from the user message.
    Parameters:
        message_text (str): The incoming message text.
    Returns:
        dict: A dictionary containing the identified intent and extracted parameters.
    """
    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={"text": message_text}
    )
    if response.status_code == 200:
        data = response.json()
        return {
            "intent": data.get("intent", "unknown"),
            "parameters": data.get("parameters", {})
        }
    else:
        print(f"GROQ API Error: {response.status_code} - {response.text}")
        return {"intent": "unknown", "parameters": {}}

# WhatsApp Interaction Functions

def send_whatsapp_message(to, message):
    """
    Send a message via WhatsApp Business API.
    Parameters:
        to (str): Recipient's WhatsApp number in E.164 format.
        message (str): Text message to send.
    Returns:
        dict: API response.
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    return response.json()

# Webhook Endpoint for Incoming Messages
@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    Handle incoming messages from WhatsApp.
    """
    data = await request.json()

    # Extract message details
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                message = change["value"].get("messages", [])[0]
                from_number = message["from"]  # Sender's WhatsApp number
                message_text = message["text"]["body"]  # Message text

                # Process the message
                response_text = process_user_message(from_number, message_text)

                # Send a response
                send_whatsapp_message(from_number, response_text)

    except Exception as e:
        print(f"Error processing message: {e}")

    return {"status": "received"}

# Message Processing

def process_user_message(user_id, message_text):
    """
    Process the user's message and determine the appropriate response.
    Parameters:
        user_id (str): The sender's WhatsApp number.
        message_text (str): The incoming message text.
    Returns:
        str: The response message text.
    """
    # Use GROQ API to determine intent and extract parameters
    groq_result = get_intent_and_parameters_from_groq(message_text)
    intent = groq_result.get("intent")
    parameters = groq_result.get("parameters", {})

    # Route based on intent
    if intent == "greeting":
        return send_greeting(user_id)

    elif intent == "property_query":
        # Use extracted parameters if available
        criteria = {
            "businessId": "b1",
            "location": parameters.get("location", "NY"),
            "budget": parameters.get("budget", 2000),
            "propertyType": parameters.get("propertyType", "apartment")
        }
        response = handle_property_availability_query(criteria)
        if response["status"] == "success":
            properties = response["properties"]
            return f"We found {len(properties)} properties for you!"
        else:
            suggestions = response.get("suggestions", [])
            return f"No exact match found. Here are {len(suggestions)} similar properties."

    elif intent == "query_error":
        return handle_query_error(message_text).get("message", "An error occurred.")

    elif intent == "multilingual_query":
        return handle_multilingual_query(user_id, message_text)

    else:
        return "Sorry, I didn't understand that. How can I assist you?"

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
