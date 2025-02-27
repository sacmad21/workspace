# from flask import Flask, request

import logging
import azure.functions as func
from azure.functions import HttpRequest, HttpResponse
import json
import os
import traceback

from clinicBot.util.util import send_whatsapp_message
from clinicBot.appointment.schedule_appointment import handle_schedule, process_schedule
from clinicBot.appointment.cancel_appointment import handle_cancel, process_cancel
from clinicBot.appointment.reschedule_appointment import handle_reschedule, process_reschedule
from clinicBot.appointment.list_appointments import handle_list_appointments

#from clinicBot.support.ask_me import handle_ask_me, process_ask_me, stop_ask_me

CLINIC= "Kalparau Clinic"

WEBHOOK_VERIFY_TOKEN = "BINGO"

# Store user states (Temporary In-Memory, Use DB for production)
user_state = {}



def post_webhook(req: func.HttpRequest) -> func.HttpResponse:
    """
    Handles incoming WhatsApp messages and routes to workflows.
    """

#    message_data = req_body["entry"][0]    ["changes"][0]["value"]["messages"][0]        
#    phone_number = message_data["from"]
#    message_text = message_data["text"]["body"].strip().lower()

    try:
        data = req.get_json()
        wa_message = ""
        print("Incomding Data :" , data)


        if "entry" in data:
            for entry in data["entry"]:
                for change in entry["changes"]:
                    if "messages" in change["value"]:
                        for message in change["value"]["messages"]:

                            print("Incomding message :" , message)

                            sender = message["from"]
                            message_text = message.get("text", {}).get("body", "").strip().lower()

                            print("Sender::", sender)
                            print("Message::", message_text)

                            # Check if user is in an active workflow
                            if (sender in user_state) and ("workflow" in user_state[sender].keys()) :                                

                                current_workflow = user_state[sender]["workflow"]
                                
                                print("Current Workflow::", current_workflow)                               
                                
                                if  current_workflow == "schedule":    
                                    wa_message = process_schedule(sender, message_text)
                                elif current_workflow == "cancel":
                                    wa_message = process_cancel(sender, message_text)
                                elif current_workflow == "reschedule":
                                    wa_message = process_reschedule(sender, message_text)
                                elif current_workflow == "ask_me":
                                    if message_text == "stop":                                        
                                        print("Stop the Q/A")
                                        #stop_ask_me(sender)
                                    else:
                                        print("Continue the Q/A")
                                        #process_ask_me(sender, message_text)
                                
                                if  wa_message.startswith("Done") :                    
                                    del user_state[sender]["workflow"]
                                    
                                return func.HttpResponse(body=json.dumps({"status": "success", "message": wa_message}), mimetype="application/json")

                            # Show main menu when user sends "hi" or "hello"
                            if message_text in ["hi", "hello"]:
                                buttons = [
                                    ("schedule", "Schedule Appointment"), 
                                    ("cancel", "Cancel Appointment"), 
#                                    ("reschedule", "Reschedule Appointment"),
                                    ("list", "List My Appointments"),
                                    ("ask_me", "Ask Me")  # NEW BUTTON
                                ]
                                wa_message = f"Welcome {CLINIC}, We will help you to schedule,reschedule and cancel appointments. What should I do for you ?"
                                send_whatsapp_message(sender, wa_message,buttons)

                            # Start different workflows and store state
                            elif message_text.lower().startswith("schedule"):
                                user_state[sender] = {"workflow": "schedule", "step": 1}
                                response = handle_schedule(sender)
                                wa_message =  response 
                            
                            elif message_text.lower().startswith("cancel"):
                                user_state[sender] = {"workflow": "cancel", "step": 1}
                                response = handle_cancel(sender)
                                wa_message =  response
                            
                            elif message_text.lower().startswith("reschedule"):
                                user_state[sender] = {"workflow": "reschedule", "step": 1}
                                response = handle_reschedule(sender)
                                wa_message =  response

                            elif message_text.lower().startswith("list"):
                                response = handle_list_appointments(sender)
                                wa_message =  response 
                            
                            elif message_text.lower().startswith("ask_me"):  # NEW FEATURE
                                user_state[sender] = {"workflow": "ask_me", "step": 1}
                                #response = handle_ask_me(sender)
                                wa_message =  response 

                            else:
                                wa_message = "Please choose an option from the menu. If you want to start conversation again then say Hi."
#                               wa_message = "Please choose an option from the menu."
                                send_whatsapp_message(sender, wa_message)

        if  wa_message.startswith("Done") :                    
            del user_state[sender]["workflow"]

        body=json.dumps({"status": "success", "message": wa_message})
        logging.info(f"\n\nResponse:::::::::::::::::::::::::::::::::::::::::\n {body}" )
        return func.HttpResponse(body=body, mimetype="application/json")


    except Exception as e:
        traceback.print_exc() 
        logging.error(f"Error processing WhatsApp message: {str(e)}")
        return func.HttpResponse(body=json.dumps({"status": "success", "message": "We will get back to you shortly." }), mimetype="application/json")




# Function for handling GET requests (webhook verification)
def get_webhook(req: HttpRequest) -> HttpResponse:
    
    WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")

    mode = req.params.get("hub.mode")
    token = req.params.get("hub.verify_token")
    challenge = req.params.get("hub.challenge")

    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        logging.info("Webhook verified successfully!")
        return HttpResponse(challenge, status_code=200)
    else:
        return HttpResponse("Forbidden", status_code=403)
