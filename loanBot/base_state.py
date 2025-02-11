class BaseState:
    """Abstract base class for states."""

    def __init__(self, state_manager):
        self.state_manager = state_manager

    def handle(self, user_message, phone_number):
        """To be implemented by child states."""
        raise NotImplementedError("Handle method must be implemented in child state classes.")
