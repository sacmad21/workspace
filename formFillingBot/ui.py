import gradio as gr
import requests
import json

# WhatsApp Bot URL (local deployment of the previous Azure Function)
WHATSAPP_BOT_URL = "http://127.0.0.1:7071/api/webhook"

# Simulated WhatsApp User ID
SIMULATED_USER_ID = "917666819468"

def simulate_whatsapp_bot(user_message):
    """Simulates a WhatsApp request and response."""
    # Create the simulated WhatsApp payload
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": SIMULATED_USER_ID,
                                    "type": "text",
                                    "text": {"body": user_message}
                                }
                            ]
                        }
                    }
                ]
            }
        ]


    }

    try:
        # Send the payload to the WhatsApp bot
        response = requests.post(WHATSAPP_BOT_URL, json=payload)


        print("\nBOT RESPONSE::\n", response.json())
        # Check the response status
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("status") == "success":
                print("\nSUCCESS::\n", response_data)
                
                return f"Bot: {response_data.get('message', 'Message sent successfully')}"
            else:
                return f"Bot Error: {response_data.get('message', 'Error in processing')}"
        else:
            return f"HTTP Error: {response.status_code} - {response.reason}"


    except Exception as e:
        return f"Exception: {str(e)}"

# Gradio UI definition
def chat_interface(user_message, chat_history):
    """Handles chat communication between the user and the bot."""
    # Get the bot response
    bot_response = simulate_whatsapp_bot(user_message)

    # Update the chat history
    chat_history.append((user_message, bot_response))
    return "", chat_history


# Gradio Interface
with gr.Blocks() as app:
    gr.Markdown("""
    # WhatsAppHook-Testing App
    Simulate a conversation with the WhatsApp Bot in a controlled testing environment.
    """)

    chatbot = gr.Chatbot(label="WhatsApp Chat Simulation")
    user_input = gr.Textbox(label="Your Message", placeholder="Type your message here...")
    send_button = gr.Button("Send")

    # Bind the chat interface
    send_button.click(chat_interface, inputs=[user_input, chatbot], outputs=[user_input, chatbot])

# Run the app
if __name__ == "__main__":
    app.launch()
