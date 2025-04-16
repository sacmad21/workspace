# Import required modules
import logging
import os
import requests
from azure.functions import HttpRequest, HttpResponse
import azure.functions as func
import json
import traceback
import azure.functions as func
import json
from eligibility.util import send_whatsapp_message
from eligibility.msg_util import get_wa_data 
from datetime import datetime

WEBHOOK_VERIFY_TOKEN = "BINGO"
GRAPH_API_TOKEN = "EAARfYvT6wOgBO9qvOuzjTn5khoM2XZBfmQUqRvnMa2W1bXtDBZC8Tz03xTB1MQZABAhGZAllMx4xyIO2McBwu0nVRYQcECLDAHBDjNf2cSAaCTLthKSe2QiRGiCpqaBZBX1X50z660kHXlntsEwN8YJetR2ofGBnpdT7wX6l4OZC6EJmfFjoWsiXgEjbDBZC0xmxyTGpfJzbNlN7pMdCZBeepNMd5ZA4JczAYqwBphZCOQ"
#WHATSAPP_API_TOKEN="Bearer EAARfYvT6wOgBO9qvOuzjTn5khoM2XZBfmQUqRvnMa2W1bXtDBZC8Tz03xTB1MQZABAhGZAllMx4xyIO2McBwu0nVRYQcECLDAHBDjNf2cSAaCTLthKSe2QiRGiCpqaBZBX1X50z660kHXlntsEwN8YJetR2ofGBnpdT7wX6l4OZC6EJmfFjoWsiXgEjbDBZC0xmxyTGpfJzbNlN7pMdCZBeepNMd5ZA4JczAYqwBphZCOQ"

import os 
import traceback
from dotenv import load_dotenv
user_data = {}
load_dotenv()


def post_webhook(req: HttpRequest) -> HttpResponse:    
    """
    Azure Function HTTP trigger for WhatsApp Webhook.
    """
    try:
        print("\nReuest :::", req)
        req_body = req.get_json()
        data = req.get_json()

        print("\nReuest :::", req_body)
        
#       message_data = req_body["entry"][0]["changes"][0]["value"]["messages"][0]        
#       phone_number = message_data["from"]
#       message_text = message_data["text"]["body"].strip().lower()

        M = get_wa_data(data)

        phone_number = M["phone"]
        message_text = M["text"]
                
        
        print(f"\n\n-----------------------------WA incoming -------------------------\n")
        print(M)

        
        if message_text is None :
            print(" We have received callback from WhatApps without user mesage")
            return "No Action"
        
        print("Stage-1 : Messaged Received ", phone_number, message_text)

        if phone_number not in user_data:
            user_data[phone_number] = { "status":"started" }

        isReady, httpmsg = getReadiness(user_data, phone_number, message_text)

        if isReady == False :
            return httpmsg

        user_session = user_data[phone_number]
        wa_message = "try to provide some intputs"

        





        logging.info("Sending the final response ::: ")
        return func.HttpResponse( body =json.dumps({"status": "success", "message": wa_message}), mimetype="application/json")


    except requests.RequestException as e:
        traceback.print_exc()
        logging.error
        ("Error sending reply or marking message: %s", e)
        return func.HttpResponse(body=json.dumps({"status": "success", "message": "We will get back to you with your query as soon as possible."}), mimetype="application/json")




def getReadiness(user_data, phone_number, msg) :
    
    session = user_data[phone_number]

    if  session["status"] == "completed" :
        wa_message = f"Dear citizen, eligibility check for you is already completed."
        send_whatsapp_message(phone_number, wa_message)
        return False, func.HttpResponse(body=json.dumps({"status": "success", "message": wa_message}), mimetype="application/json")


    if  session["status"] == "started" :
        
        session["status"] = "ready"
        wa_message = "Welcome to Eligibiltiy Test for MP goverment schemes: Should we proceed ? yes / no "
        send_whatsapp_message(phone_number, wa_message)
        return False, func.HttpResponse(body=json.dumps({"status": "success", "message": wa_message}), mimetype="application/json")


    if  session["status"] == "ready" and msg.lower() == "no":
        wa_message = f"Dear citizen, please get back to us for eligibility check, whenever required"
        send_whatsapp_message(phone_number, wa_message)
        session["status"] = "started"
        
        return False, func.HttpResponse(body=json.dumps({"status": "success", "message": wa_message}), mimetype="application/json")


    if session["status"] == "ready" and msg.lower() == "yes" :
        wa_message = f"we are ready for eligibility check, Answer following questions one by one."        
        send_whatsapp_message(phone_number, wa_message)
        session["status"] = "in-progress"

    return True, func.HttpResponse(body=json.dumps({"status": "success", "message": "No Action"}), mimetype="application/json")       




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
