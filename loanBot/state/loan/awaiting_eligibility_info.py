from base_state import BaseState
from common_state_functions import collect_parameters

class AwaitingEligibilityInfo(BaseState):
    """Handles eligibility data collection via text or document upload."""

    def handle(self, user_message, phone_number, document=None):
        """
        Handles user input by:
        - Extracting parameters from text (if provided).
        - Extracting parameters from a document (if uploaded).
        - Validating and storing collected parameters.
        - Confirming with the user once all parameters are collected.
        """
        if collect_parameters(self.state_manager, phone_number, user_message, document):
            self.state_manager.transition("awaiting_eligibility_confirmation")
