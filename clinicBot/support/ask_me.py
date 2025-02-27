from clinicBot.util.util import send_whatsapp_message
#import quadrant
from qdrant_client import QdrantClient

import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QUADRANT_API_KEY = os.getenv("QUADRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")

# Initialize Quadrant Client
#quadrant_client = quadrant.Client(api_key=QUADRANT_API_KEY)

quadrant_client = QdrantClient(api_key=QUADRANT_API_KEY)
collection = quadrant_client.get_collection("midjourney")

# Initialize OpenAI LLM
openai.api_key = OPENAI_API_KEY

def handle_ask_me(sender):
    """
    Starts the Q&A session with the user.
    """
    send_whatsapp_message(sender, "You can ask me anything about medications, side effects, or usage guidelines. Type 'stop' to end the session.")

def process_ask_me(sender, message):
    """
    Retrieves relevant information from Quadrant and generates an AI-powered answer.
    """
    try:
        # Retrieve similar documents from Quadrant
        results = collection.query(text=message, top_k=3)
        context = " ".join([result["text"] for result in results])

        # Generate a response using OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a medical assistant providing accurate medication information."},
                {"role": "user", "content": f"Answer based on this context:\n{context}\n\nQuestion: {message}\nAnswer:"}
            ]
        )

        send_whatsapp_message(sender, response["choices"][0]["message"]["content"])

    except Exception as e:
        send_whatsapp_message(sender, "Sorry, I couldn't find an answer. Please try rephrasing your question.")

def stop_ask_me(sender):
    """
    Ends the Q&A session.
    """
    send_whatsapp_message(sender, "Q&A session ended. Type 'hi' to return to the main menu.")
    del user_state[sender]  # Remove from active workflows
