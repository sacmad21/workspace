from flask import Flask, request, jsonify
from state_manager import StateManager

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    user_message = data["message"]["text"]
    phone_number = data["from"]
    document = data.get("document")

    # Load user state
    user_state = StateManager(phone_number).get_state()
    
    # Process message based on state
    user_state.handle(user_message, phone_number, document)

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
