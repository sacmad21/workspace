from base_state import BaseState
from util import send_whatsapp_message

class NewState(BaseState):
    """Handles the initial user message 'Hi'."""
    
    def handle(self, user_message, phone_number):
        send_whatsapp_message(phone_number, "Welcome! Choose an option:\n✅ Loan Eligibility – [Check Now]\n✅ View Loan Rates – [View Options]\n✅ Upload Documents – [Upload Now]")
        self.state_manager.transition("waiting_for_selection")
