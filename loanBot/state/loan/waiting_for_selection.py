from base_state import BaseState
from util import send_whatsapp_message, fetch_loan_options

class WaitingForSelection(BaseState):
    """Handles selection of loan-related options."""
    
    def handle(self, user_message, phone_number):
        if user_message.lower() == "loan eligibility":
            send_whatsapp_message(phone_number, "Please enter your income and employment type (e.g., '60000 Salaried').")
            self.state_manager.transition("awaiting_eligibility_info")
        
        elif user_message.lower() == "view loan options":
            loans = fetch_loan_options()
            message = "\n".join([f"🏦 {l['bank_name']}: {l['interest_rate']}% for {l['max_tenure']} years" for l in loans])
            send_whatsapp_message(phone_number, message)
            self.state_manager.transition("awaiting_next_action")

        elif user_message.lower() == "upload documents":
            send_whatsapp_message(phone_number, "Please send the document as an attachment.")
            self.state_manager.transition("awaiting_document_upload")
