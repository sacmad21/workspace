from clinicBot.util.util import send_whatsapp_message, list_appointments
import datetime

def handle_list_appointments(sender):
    """
    Fetches and lists upcoming appointments for the user.
    """
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time

    events = list(list_appointments(sender))    

    response = "Here are your upcoming appointments:\n"


    for event in events:

        d = event["date_time"].strftime("%m/%d/%Y")

        t = event["date_time"].strftime("%H:%M:%S")
        
        eventPair = event["doctor"] + f" at {d}  on  {t}"
        
        response += f"📅 {eventPair}\n"

    if len(events) == 0 :
        response = "Sorry no appointements booked yet."

    send_whatsapp_message(sender, response)
    return response 
