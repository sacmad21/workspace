import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
import datetime
import traceback

# Load environment variables
load_dotenv()

secret_file = "botplus_secret.json"

#Google Calendar API Setup
SCOPES = ["https://www.googleapis.com/auth/calendar"]
CREDS = Credentials.from_service_account_file(secret_file, scopes=SCOPES)
calendar_service = build("calendar", "v3", credentials=CREDS)

def readEventsFromGCalender():
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    events_result = calendar_service.events().list(
        calendarId="primary", timeMin=now, maxResults=5, singleEvents=True, orderBy="startTime"
    ).execute()

    
    events = events_result.get("items", [])
    return events   


def scheduleEvent(summary, description, start_time, end_time, attendees=None):
    """
    Schedule a new event in Google Calendar.
    
    :param summary: Title of the event
    :param description: Description of the event
    :param start_time: Event start time (ISO 8601 format: YYYY-MM-DDTHH:MM:SS)
    :param end_time: Event end time (ISO 8601 format)
    :param attendees: List of attendees' email addresses (optional)
    :return: Created event details
    """
    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_time, "timeZone": "UTC"},
        "end": {"dateTime": end_time, "timeZone": "UTC"},
    }

    if attendees:
        event["attendees"] = [{"email": email} for email in attendees]

    created_event = calendar_service.events().insert(calendarId="primary", body=event).execute()
    return created_event



def list_calendars():
    """List all calendars and their IDs."""
    calendars = calendar_service.calendarList().list().execute()
    for calendar in calendars.get("items", []):
        print(f"Calendar Name: {calendar['summary']}, Calendar ID: {calendar['id']}")



list_calendars()

all = list_calendars()
print("Calenders::", all)
