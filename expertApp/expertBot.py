# Import required modules
import logging
import os
import requests
from azure.functions import HttpRequest, HttpResponse
import azure.functions as func

WEBHOOK_VERIFY_TOKEN = "BINGO"
GRAPH_API_TOKEN = "EAARfYvT6wOgBO9qvOuzjTn5khoM2XZBfmQUqRvnMa2W1bXtDBZC8Tz03xTB1MQZABAhGZAllMx4xyIO2McBwu0nVRYQcECLDAHBDjNf2cSAaCTLthKSe2QiRGiCpqaBZBX1X50z660kHXlntsEwN8YJetR2ofGBnpdT7wX6l4OZC6EJmfFjoWsiXgEjbDBZC0xmxyTGpfJzbNlN7pMdCZBeepNMd5ZA4JczAYqwBphZCOQ"

from expertApp.MPF_app import answerInSpecific

def post_webhook(req: HttpRequest) -> HttpResponse:
    try:
        body = req.get_json()
        logging.info("Incoming webhook message: %s", body)

        # Extract message and other details
        message = body.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [{}])[0]
        if not message or message.get("type") != "text":
            return HttpResponse("No text message to process", status_code=200)

        business_phone_number_id = body.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("metadata", {}).get("phone_number_id")

        prompt = message.get("text", {}).get("body", "")

        bot_response = answerInSpecific(prompt, "sess001",  "divorce")
        
        # Send reply message
        try:
            url = f"https://graph.facebook.com/v18.0/{business_phone_number_id}/messages"
            headers = {"Authorization": f"Bearer {GRAPH_API_TOKEN}"}
            data = {
                "messaging_product": "whatsapp",
                "to": message["from"],
                "text": {"body": bot_response},
                "context": {"message_id": message["id"]},
            }
            requests.post(url, headers=headers, json=data)


            # Mark the message as read
            #mark_read_data = {
            #    "messaging_product": "whatsapp",
            #    "status": "read",
            #    "message_id": message["id"],
            #}
            #requests.post(url, headers=headers, json=mark_read_data)

        except requests.RequestException as e:
            logging.error("Error sending reply or marking message: %s", e)

        return HttpResponse("Message processed", status_code=200)
    except Exception as e:
        logging.error("Error processing request: %s", e)
        return HttpResponse("Internal Server Error", status_code=500)



# Function for handling GET requests (webhook verification)
def get_webhook(req: HttpRequest) -> HttpResponse:
    mode = req.params.get("hub.mode")
    token = req.params.get("hub.verify_token")
    challenge = req.params.get("hub.challenge")

    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        logging.info("Webhook verified successfully!")
        return HttpResponse(challenge, status_code=200)
    else:
        return HttpResponse("Forbidden", status_code=403)
