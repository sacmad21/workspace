from clinicBot.util.util import send_whatsapp_message

reschedule_requests = {}



def handle_reschedule(sender):
    """
    Starts the rescheduling workflow.
    """
    send_whatsapp_message(sender, "Please provide the date & time of the appointment you want to reschedule.")
    reschedule_requests[sender] = {"step": 1}



def process_reschedule(sender, message):
    """
    Processes the rescheduling request.
    """
    if sender in reschedule_requests and reschedule_requests[sender]["step"] == 1:
        reschedule_requests[sender]["old_appointment"] = message
        reschedule_requests[sender]["step"] = 2
        send_whatsapp_message(sender, "Provide the new date & time for the reschedule.")

    elif sender in reschedule_requests and reschedule_requests[sender]["step"] == 2:
        reschedule_requests[sender]["new_appointment"] = message
        send_whatsapp_message(sender, f"Your appointment has been rescheduled to {message}.")
        
        del reschedule_requests[sender]  # Remove user from state
