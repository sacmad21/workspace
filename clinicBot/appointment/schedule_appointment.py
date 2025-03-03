import datetime
import random
from clinicBot.util.util import send_whatsapp_message, book_appointment, getAppointments
import traceback
import logging 
import random


appointments = {}

def handle_schedule(sender):
    """
    Starts the appointment scheduling workflow by asking for the doctor's name first.
    """
    wa_message = "Please provide the doctor's name."
    send_whatsapp_message(sender, wa_message)
    appointments[sender] = {"step": 1}
    return wa_message


def process_schedule(sender, message):

    """
    Processes the scheduling steps.
    """
    user_data = appointments.get(sender, {})
    wa_message = ""
    print("Schedule Step :", user_data.get("step"), "Message::", message)  


    if user_data.get("step") == 1:
        user_data["doctor"] = message.title()
        user_data["step"] = 2
        wa_message = f"Got it! Please provide the date you want an appointment with Dr. {user_data['doctor']} (DD-MM-YYYY)."
        send_whatsapp_message(sender, wa_message)
        return wa_message


    elif user_data.get("step") == 2:
        try:
            user_data["step"] = 3
            user_data["date"] = datetime.datetime.strptime(message, "%d-%m-%Y").date()

            # Fetch doctor-specific available time slots            
            available_slots = get_available_time_slots(user_data["doctor"], user_data["date"])
            recommended_slots = available_slots[:2]

            user_data["available_slots"] = available_slots
            user_data["recommended_slots"] = recommended_slots


            print("Recommended Slots ::", recommended_slots)
            buttons = [(slot, slot) for slot in recommended_slots] + [("other", "Other")]
            wa_message = f"Dr. {user_data['doctor']} is available at these times. Choose one or ask for others"
#           send_whatsapp_message(sender, wa_message, buttons
            send_whatsapp_message(sender, wa_message,buttons)
        except ValueError:
            wa_message ="Invalid date format. Please enter in DD-MM-YYYY format."
            send_whatsapp_message(sender, wa_message)
        return wa_message


    elif user_data.get("step") == 3:
        if message.lower() == "other" :
            # remove the recommended slots from available slots.
            # randomize the availables slots and remove 3 slots from it.
            available_slots = user_data["available_slots"]
            recommended_slots = user_data["recommended_slots"]

            available_slots =  [i for i in available_slots if i not in recommended_slots]
            random.shuffle(available_slots)
            recommended_slots = available_slots[:2]

            user_data["available_slots"] = available_slots
            user_data["recommended_slots"] = recommended_slots

            print("Recommended Slots ::", recommended_slots)
            buttons = [(slot, slot) for slot in recommended_slots] + [("other", "Other (Type Custom Time)")]
            wa_message = f"Choose one or type your own:"
            send_whatsapp_message(sender, wa_message,buttons)

        elif message.upper() in user_data.get("recommended_slots", []):
            user_data["step"] = 4
            user_data["selected_slot"] = message.upper()

            buttons = [("yes","Yes"),("no","No")]
            wa_message = f"You appointment with Dr. {user_data['doctor']} is scheduled at {message.upper()}, Confirm"
            send_whatsapp_message(sender, wa_message, buttons)

        else:
            wa_message = "Invalid selection. Please select a valid slot."
            send_whatsapp_message(sender, wa_message)
        return wa_message

    elif user_data.get("step") == 4:
        try:
            print("Confirmation Step ", message, ":")

            if message.lower() == "yes" :
                # Instantly book appointment for selected slot

                user_data["time"] = datetime.datetime.strptime(user_data["selected_slot"], "%I:%M %p").time()
                
                final_datetime = datetime.datetime.combine(user_data["date"], user_data["time"])

                print("Write to DB ::", sender, "-", user_data["doctor"], "-", final_datetime)
                msg = book_appointment(sender, user_data["doctor"],final_datetime)

                if msg.lower() == "success"  :
                    wa_message = f"Done-Appointment confirmed with Dr. {user_data['doctor']} on {final_datetime.strftime('%Y-%m-%d %I:%M %p')}."
                    send_whatsapp_message(sender, wa_message)
                    del appointments[sender]
                else :
                    wa_message = f"Done - Somethin gone wrong, try after sometime."
                    send_whatsapp_message(sender, wa_message)
                    user_data["step"] = 1
                    del appointments[sender]

            elif message.lower() == "no" :
                wa_message = f"Let's start again for scheduling appointment"
                user_data["step"] = 1
                send_whatsapp_message(sender, wa_message)
            else: 
                wa_message = "Invalid selection. Please select a Yes/No "
                send_whatsapp_message(sender, wa_message)


        except ValueError:
            traceback.print_exc() 
            wa_message =  "Invalid format. Please enter time in HH:MM AM/PM format."
            send_whatsapp_message(sender, wa_message)
    
    return wa_message




def get_available_time_slots(doctor, date):
    """
    Fetches available 30-minute time slots for a specific doctor on a given date.
    """
    print("Finding available Time slots" , date)
    try:
        existing_appointments = getAppointments(doctor,date)

        booked_times = {appointment["date_time"].time() for appointment in existing_appointments}
        
        start_hour = 9  # Clinic opens at 9 AM
        end_hour = 17  # Clinic closes at 5 PM

        available_slots = []
        for hour in range(start_hour, end_hour):
            for minute in [0, 30]:  # 30-minute slots
                slot_time = datetime.time(hour, minute)
                if slot_time not in booked_times:
                    print("Free slot found ::", slot_time)
                    available_slots.append(slot_time.strftime("%I:%M %p"))

        random.shuffle(available_slots)

        return available_slots  # Return top 3 available slots

    except Exception as e:
        print("\nError occured :::", e)
        traceback.print_exc() 
        logging.error(f"Error processing WhatsApp message: {str(e)}")
        return "No Free Slots visible availale"




    