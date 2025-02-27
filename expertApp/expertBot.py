# Import required modules
import logging
import os
import requests
from azure.functions import HttpRequest, HttpResponse
import azure.functions as func
import json
import traceback

WEBHOOK_VERIFY_TOKEN = "BINGO"
GRAPH_API_TOKEN = "EAARfYvT6wOgBO9qvOuzjTn5khoM2XZBfmQUqRvnMa2W1bXtDBZC8Tz03xTB1MQZABAhGZAllMx4xyIO2McBwu0nVRYQcECLDAHBDjNf2cSAaCTLthKSe2QiRGiCpqaBZBX1X50z660kHXlntsEwN8YJetR2ofGBnpdT7wX6l4OZC6EJmfFjoWsiXgEjbDBZC0xmxyTGpfJzbNlN7pMdCZBeepNMd5ZA4JczAYqwBphZCOQ"
#WHATSAPP_API_TOKEN="Bearer EAARfYvT6wOgBO9qvOuzjTn5khoM2XZBfmQUqRvnMa2W1bXtDBZC8Tz03xTB1MQZABAhGZAllMx4xyIO2McBwu0nVRYQcECLDAHBDjNf2cSAaCTLthKSe2QiRGiCpqaBZBX1X50z660kHXlntsEwN8YJetR2ofGBnpdT7wX6l4OZC6EJmfFjoWsiXgEjbDBZC0xmxyTGpfJzbNlN7pMdCZBeepNMd5ZA4JczAYqwBphZCOQ"


from expertApp.MPF_app import answerInSpecific

def post_webhook(req: HttpRequest) -> HttpResponse:
    
    try:
        body = req.get_json()
        logging.info("Incoming webhook message: %s", body)

        # Extract message and other details
        message = body.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [{}])[0]

        if not message or message.get("type") != "text":
            return HttpResponse("No text message to process", status_code=200)

        logging.info("Message body::", message)

        business_phone_number_id = body.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("metadata", {}).get("phone_number_id")
#       business_phone_number_id = "441143062411889"

        prompt = message.get("text", {}).get("body", "")

        print("business_phone_number_id=" ,  business_phone_number_id , "\tPrompt=" + prompt)

#       print("Message body::", message , "\nBusinness Phone Id=", business_phone_number_id, "\tPrompt=", prompt)

        # bot_response = answerInSpecific(prompt, "sess001",  "divorce")
        bot_response = answerInSpecific(prompt,   "sess001",  "mp_finance_faq_csv")
        # bot_response = answerInSpecific(prompt, "sess001",  "MPdata")
        
        logging.info("Bot Response::" + bot_response)

        # Send reply message

        url = f"https://graph.facebook.com/v18.0/{business_phone_number_id}/messages"
        headers = {"Authorization": f"Bearer {GRAPH_API_TOKEN}"}
        data = {
            "messaging_product": "whatsapp",
            "to": message["from"],
            "text": {"body": bot_response},
#           "context": {"message_id": message["id"]},
            }
        
        requests.post(url, headers=headers, json=data)

        # Mark the message as read
        #mark_read_data = {
        #    "messaging_product": "whatsapp",
        #    "status": "read",
        #    "message_id": message["id"],
        #}
        #requests.post(url, headers=headers, json=mark_read_data)
        
        logging.info("Sending the final response ::: ")
        return func.HttpResponse( body =json.dumps({"status": "success", "message": bot_response}), mimetype="application/json")


    except requests.RequestException as e:
        traceback.print_exc()
        logging.error
        ("Error sending reply or marking message: %s", e)
        return func.HttpResponse(body=json.dumps({"status": "success", "message": "We will get back to you with your query as soon as possible."}), mimetype="application/json")



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
