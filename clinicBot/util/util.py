import os
from pymongo import MongoClient
import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import timedelta
import datetime
import traceback

from whatsAppTokens import tokens


# Load environment variables
load_dotenv()

# Azure Cosmos DB MongoDB API Configuration
COSMOS_DB_URI = os.getenv("COSMOS_DB_URI")

COSMOS_DB_NAME = "clinic_db"
COSMOS_COLLECTION_NAME = "appointements"

# Connect to Azure Cosmos DB
client = MongoClient(COSMOS_DB_URI)
db = client[COSMOS_DB_NAME]
appointments_collection = db[COSMOS_COLLECTION_NAME]

#Google Calendar API Setup
SCOPES = ["https://www.googleapis.com/auth/calendar"]
CREDS = Credentials.from_service_account_file("botplus_secret.json", scopes=SCOPES)
calendar_service = build("calendar", "v3", credentials=CREDS)


# WhatsApp API Configuration
wa_vars = tokens["ClinicApp"]

print("\n\n ----------- Interactive :: ", os.getenv("WHATSAPP_INTERACTIVE_MESSAGE") )

WHATSAPP_API_BASE_URL = os.getenv("WHATSAPP_API_BASE_URL")
WHATSAPP_INTERACTIVE_MESSAGE = True if os.getenv("WHATSAPP_INTERACTIVE_MESSAGE").lower() == "true" else False

WHATSAPP_CLOUD_API_PHONE_NUMBER_ID = wa_vars["WA_Phone_Number_ID"]
WHATSAPP_TOKEN = wa_vars["WA_Token"]


def send_whatsapp_message(recipient_id, message, buttons=None):
    """
    Sends a WhatsApp message with optional interactive buttons.
    """

    print("\n WHATSAPP_INTERACTIVE_MESSAGE ::", WHATSAPP_INTERACTIVE_MESSAGE)
    url = f"{WHATSAPP_API_BASE_URL}/{WHATSAPP_CLOUD_API_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    button_txt = " "

    if buttons and WHATSAPP_INTERACTIVE_MESSAGE == False:
        button_list =  [key for key, _ in buttons]
        button_txt = " Options:" + ", ".join(button_list)

    data = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message + button_txt }
    }

    if buttons and WHATSAPP_INTERACTIVE_MESSAGE:
        data["type"] = "interactive"
        data["interactive"] = {
            "type": "button",
            "action": {"buttons": [{"type": "reply", "reply": {"id": btn_id, "title": btn_text}} for btn_id, btn_text in buttons]},
            "body": {"text": message},
        }

    

    print("WA URL", url)
    print("WA Messge::", data)

    requests.post(url, headers=headers, json=data)


def getAppointments(doctor,date):
    slots = appointments_collection.find({"doctor": doctor, "date_time": {"$gte": datetime.datetime.combine(date, datetime.time(0, 0)), "$lt": datetime.datetime.combine(date, datetime.time(23, 59))}})
    return slots


def cancel_appointment(sender, date_string):
    """
    Instantly deletes an appointment for a selected time slot.
    """

    datetime_object = datetime.datetime.strptime(date_string, "%d-%m-%Y")

    datetime_object = datetime_object + timedelta(days=1)

    query = {"patient_number": sender, 
                "date_time": {"$gte": datetime_object}, 
                    "date_time" : {"$lte": datetime_object} }
    count = appointments_collection.delete_many(query)
    return count


def list_appointments(sender) :    
    """
    Instantly list all the appointments for a client.
    """

    print("List all appointmennts :: ", sender)
    slots = appointments_collection.find({"patient_number": sender})

    return slots



def readEventsFromGCalender():
        
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    events_result = calendar_service.events().list(
        calendarId="primary", timeMin=now, maxResults=5, singleEvents=True, orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])
    return events 



def book_appointment(sender, doctor, final_datetime):
    """
    Instantly books an appointment for a selected time slot.
    """
    print("Book the appointmennt :: ", sender, doctor, final_datetime)

    try:
        appointment_data = {
            "patient_number": sender,
            "doctor": doctor,
            "date_time": final_datetime,
            "status": "confirmed"
        }
        appointments_collection.insert_one(appointment_data)

    except Exception as e:
        print("\nError occured during Appointment DB operations:::", e)
        traceback.print_exc() 
        return "Fail"
        
    return "Success"


x = datetime.datetime.now()
msg = book_appointment("919819436007","Dr Mugdha",x )
print(msg)