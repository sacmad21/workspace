from base_state import BaseState
from common_state_functions import handle_rag_query

class AwaitingLoanOptions(BaseState):
    """Handles loan-related Q/A using RAG."""

    def handle(self, user_message, phone_number):
        """
        Checks if `Support_QA = RAG` and processes Q/A queries.
        If Q/A mode is not enabled, proceeds to loan option selection.
        """

        # Check if the message should be handled as a Q/A query
        if handle_rag_query(self.state_manager, phone_number, user_message):
            return  # Q/A mode is active, so we don't process anything else

        # Default behavior for loan selection (if needed)
        send_whatsapp_message(phone_number, "Please choose a loan option or ask a question.")
