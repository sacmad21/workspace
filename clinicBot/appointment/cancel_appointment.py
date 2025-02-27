from clinicBot.util.util import send_whatsapp_message, cancel_appointment

cancel_requests = {}

def handle_cancel(sender):
    """
    Starts the appointment cancellation workflow.
    """
    wa_message = "Please provide the date & time of the appointment you want to cancel."
    send_whatsapp_message(sender, wa_message)
    cancel_requests[sender] = {"step": 1}
    return wa_message 



def process_cancel(sender, message):
    """
    Processes the cancellation request.
    """
    wa_message = "Cancelling"

    if sender in cancel_requests and cancel_requests[sender]["step"] == 1:
        cancel_requests[sender]["appointment"] = message

        result = cancel_appointment(sender, message)

        if result.deleted_count == 1 :
            wa_message = f"Done, Your appointment on {message} is canceled."
        elif result.deleted_count > 1 :
            wa_message = f"Done, Your {result.deleted_count} appointements are canceled."
        else :
            wa_message = f"Done, But No appointements found for {sender}."

        
        send_whatsapp_message(sender, wa_message)

        del cancel_requests[sender]  # Remove user from state

    return wa_message