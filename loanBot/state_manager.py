import logging
import traceback
import json
import os

# Initialize Logger
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.DEBUG
)

# Load State Configuration from JSON
STATE_CONFIG_FILE = "loanBot/state/loan/state_config.json"

try:
    with open(STATE_CONFIG_FILE, "r") as file:
        STATE_CONFIG = json.load(file)
except Exception as e:
    logging.error(f"❌ Failed to load state_config.json: {str(e)}")
    logging.error(traceback.format_exc())
    STATE_CONFIG = {}

# In-memory storage for user states
USER_STATES = {}





# ===========================
# 🔹 Class: StateManager (In-Memory)
# ===========================

class StateManager:
    """
    Manages user states and data using an in-memory dictionary.
    """

    def __init__(self, phone_number):
        """
        Initializes the StateManager with the user's phone number.
        Loads the user's current state from memory or sets default state.
        """
        self.phone_number = phone_number

        # Load user state or initialize default state
        if phone_number in USER_STATES:
            self.state_data = USER_STATES[phone_number]
            self.state_name = self.state_data.get("state", "awaiting_eligibility_info")
        else:
            self.state_data = {"state": "awaiting_eligibility_info", "data": {}}
            self.state_name = "awaiting_eligibility_info"
            USER_STATES[phone_number] = self.state_data

        logging.info(f"📢 Initialized StateManager for {phone_number}, Current State: {self.state_name}")



    # ===========================
    # 🔹 Function: Get Current State Handler
    # ===========================

    def get_state(self):
        """
        Retrieves the current state handler based on the stored state.
        Returns:
        - dict: State configuration from STATE_CONFIG
        """
        return STATE_CONFIG.get(self.state_name, {})



    # ===========================
    # 🔹 Function: Save State in Memory
    # ===========================

    def save_state(self):
        """
        Saves the user's current state data to the in-memory storage.
        """
        try:
            USER_STATES[self.phone_number] = self.state_data
            logging.info(f"✅ State saved for {self.phone_number}: {self.state_data}")
        except Exception as e:
            logging.error(f"❌ Error saving state for {self.phone_number}: {str(e)}")
            logging.error(traceback.format_exc())



    # ===========================
    # 🔹 Function: Update User Data in State
    # ===========================

    def update_state(self, new_data):
        """
        Updates the user's state data with new information.
        - new_data (dict): Dictionary containing updated user data.
        """
        try:
            logging.info(f"🔄 Updating state for {self.phone_number}: {new_data}")
            self.state_data["data"].update(new_data)
            self.save_state()
        except Exception as e:
            logging.error(f"❌ Error updating state for {self.phone_number}: {str(e)}")
            logging.error(traceback.format_exc())


    # ===========================
    # 🔹 Function: Get Stored User Data
    # ===========================
    def get_data(self):
        """
        Retrieves the stored user data from the current state.
        Returns:
        - dict: User data stored in the state
        """
        return self.state_data.get("data", {})



    # ===========================
    # 🔹 Function: Check for Missing Required Parameters
    # ===========================
    def get_missing_params(self):
        """
        Identifies missing required parameters for the current state.
        Returns:
        - list: List of missing parameter names
        """
        try:
            state_config = self.get_state()
            parameters = state_config.get("parameters", {})
            user_data = self.get_data()

            missing_params = [
                param for param, config in parameters.items()
                if config.get("required", False) and param not in user_data
            ]

            if missing_params:
                logging.warning(f"⚠️ Missing parameters for {self.phone_number}: {missing_params}")

            return missing_params

        except Exception as e:
            logging.error(f"❌ Error checking missing parameters for {self.phone_number}: {str(e)}")
            logging.error(traceback.format_exc())
            return []



    # ===========================
    # 🔹 Function: Transition to Next State
    # ===========================

    def transition(self, next_state):
        """
        Transitions the user to the specified next state.
        - next_state (str): The next state to transition to.
        """
        try:
            if next_state not in STATE_CONFIG:
                logging.error(f"❌ Invalid state transition for {self.phone_number}: {next_state} does not exist.")
                return False

            logging.info(f"🔄 Transitioning {self.phone_number} from {self.state_name} to {next_state}")

            # Log state exit
            if "logging" in STATE_CONFIG[self.state_name] and "on_exit" in STATE_CONFIG[self.state_name]["logging"]:
                logging.info(STATE_CONFIG[self.state_name]["logging"]["on_exit"])

            # Update state
            self.state_name = next_state
            self.state_data["state"] = next_state
            self.save_state()

            # Log state entry
            if "logging" in STATE_CONFIG[next_state] and "on_enter" in STATE_CONFIG[next_state]["logging"]:
                logging.info(STATE_CONFIG[next_state]["logging"]["on_enter"])

            return True

        except Exception as e:
            logging.error(f"❌ Error transitioning state for {self.phone_number}: {str(e)}")
            logging.error(traceback.format_exc())
            return False
