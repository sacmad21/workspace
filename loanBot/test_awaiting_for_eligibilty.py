import logging
import json
from state_manager import StateManager
from state.loan.awaiting_eligibility_info import  AwaitingEligibilityInfo  # Import state function

# Load State Configuration
STATE_CONFIG_FILE = "loanBot/state/loan/state_config.json"
                     
try:
    with open(STATE_CONFIG_FILE, "r") as file:
        STATE_CONFIG = json.load(file)
except Exception as e:
    logging.error(f"❌ Failed to load state_config.json: {str(e)}")
    STATE_CONFIG = {}



# ===========================
# 🔹 Test Function: Simulate User Conversation with Bot
# ===========================

def simulate_conversation(contact_number, user_inputs):
    """
    Simulates a chatbot conversation for the `awaiting_eligibility_info` state.

    Parameters:
    - phone_number (str): The user's phone number.
    - user_inputs (list): A list of user messages simulating a conversation.

    Returns:
    - None
    """
    state_manager = StateManager(contact_number)

    print("\n📢 Starting Test Conversation:")
    print(f"📲 User: Hi\n🤖 Bot: Welcome! Please provide your eligibil`ity details.")

    state = AwaitingEligibilityInfo(state_manager)

    for msg in user_inputs:
        bot_response = state.handle(phone_number=contact_number, user_message=msg)
        print(f"📲 User: {msg}\n🤖 Bot: {bot_response}")

    print("\n🎉 Test Conversation Completed!\n")




# ===========================
# 🔹 Test Case 1: Complete Info in One Go
# ===========================

def test_complete_info_in_one_go():
    """
    Tests when the user provides all required details in a single message.
    """
    phone_number = "+917666819468"
    user_inputs = ["Income: 75000, Employment: Salaried, Aadhaar: 234567890123, PAN: ABCDE1234F"]
    simulate_conversation(phone_number, user_inputs)




# ===========================
# 🔹 Test Case 2: Partial Info with Follow-ups
# ===========================

def test_partial_info_with_follow_ups():
    """
    Tests when the user provides details in multiple steps.
    """
    phone_number = "+917666819468"
    user_inputs = [
        "Income: 60000",  # User provides income only
        "Employment: Self-Employed",  # Next input provides employment type
        "Aadhaar: 234567890123",  # Next, Aadhaar
        "PAN: ABCDE1234F"  # Finally, PAN
    ]
    simulate_conversation(phone_number, user_inputs)




# ===========================
# 🔹 Test Case 3: Incorrect Input with Corrections
# ===========================

def test_incorrect_input_with_corrections():
    """
    Tests when the user provides incorrect data and then corrects it.
    """
    phone_number = "+917666819468"
    user_inputs = [
        "Income: seventy thousand",  # Invalid input
        "Income: 70000",  # Corrected input
        "Employment: Freelancer",  # Invalid employment type
        "Employment: Salaried",  # Corrected employment type
        "Aadhaar: 123456789012",  # Invalid Aadhaar
        "Aadhaar: 234567890123",  # Corrected Aadhaar
        "PAN: 1234ABCDE5",  # Invalid PAN
        "PAN: ABCDE1234F"  # Corrected PAN
    ]
    simulate_conversation(phone_number, user_inputs)




# ===========================
# 🔹 Run Test Cases
# ===========================

if __name__ == "__main__":
    print("\n🚀 Running Tests for `awaiting_eligibility_info()`...")
#    test_complete_info_in_one_go()
    test_partial_info_with_follow_ups()
#    test_incorrect_input_with_corrections()
    print("\n✅ All Test Cases Executed!")
