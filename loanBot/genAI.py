import json
import requests

from config import TOGETHER_GENAI_API_KEY
from qdrant_client import QdrantClient
from config import QDRANT_URL



import requests
from config import TOGETHER_GENAI_API_KEY

# Load schema dynamically
with open("propertyConfig.json", "r") as f:
    PROPERTY_SCHEMA = json.load(f)

  

def extract_parameters_from_document(document_url, state_name):
    """
    Uses GenAI Vision API to extract relevant fields from a document.
    """
    parameters = STATE_CONFIG.get(state_name, {}).get("parameters", {}).keys()

    prompt = f"Extract the following details from the uploaded document: {', '.join(parameters)}."

    url = "https://api.together.xyz/vision/extract"
    headers = {
        "Authorization": f"Bearer {TOGETHER_GENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "document_url": document_url,
        "prompt": prompt,
        "max_tokens": 100
    }

    response = requests.post(url, headers=headers, json=data).json()

    try:
        extracted_data = response.get("text", "{}")
        return eval(extracted_data)
    except Exception as e:
        print(f"Error parsing GenAI Vision response: {e}")
        return {}


def extract_parameters_from_text(user_message, state_name):
    """
    Uses GenAI NLP to extract relevant parameters from user text.
    """
    parameters = STATE_CONFIG.get(state_name, {}).get("parameters", {}).keys()

    prompt = f"Extract the following details from the user's message: {', '.join(parameters)}."

    url = "https://api.together.xyz/generate"
    headers = {"Authorization": f"Bearer {TOGETHER_GENAI_API_KEY}", "Content-Type": "application/json"}
    data = {"prompt": prompt, "max_tokens": 100}

    response = requests.post(url, headers=headers, json=data).json()

    try:
        extracted_data = response.get("text", "{}")
        return eval(extracted_data)  # Convert JSON string to dictionary
    except Exception as e:
        print(f"Error parsing GenAI NLP response: {e}")
        return {}






def extract_query_parameters(user_message, cosmos_config):
    """
    Extracts query parameters from user input using GenAI.
    - Uses `propertyConfig.json` dynamically instead of a hardcoded schema.
    - Determines if the query is complex (i.e., requires aggregation or advanced logic).
    """

    schema_description = json.dumps(PROPERTY_SCHEMA, indent=2)

    prompt = f"""
    Given the following MongoDB schema:

    Schema:
    {schema_description}

    User Query: "{user_message}"

    1️⃣ If the query can be mapped to structured fields, extract parameters in JSON format.
    2️⃣ If the query is complex (e.g., requires aggregation, max/min functions, ranking), return:
        {{
            "complex_query": true
        }}

    Example Outputs:
    ✅ Simple Query: {{"bhk": 2, "location.city": "Mumbai"}}
    ✅ Complex Query: {{"complex_query": true}}
    """

    url = "https://api.together.xyz/generate"
    headers = {"Authorization": f"Bearer {TOGETHER_GENAI_API_KEY}", "Content-Type": "application/json"}
    data = {"prompt": prompt, "max_tokens": 150}

    response = requests.post(url, headers=headers, json=data).json()

    try:
        extracted_data = response.get("text", "{}")
        return json.loads(extracted_data)  # Convert JSON string to dictionary
    except Exception as e:
        print(f"Error parsing GenAI response: {e}")
        return {}



def generate_rag_response(query, collection_name, top_k=1):
    """
    Fetches the most relevant document(s) from Qdrant Vector DB for the given query.
    - Uses `top_k` from the state configuration to retrieve multiple relevant answers.
    """

    client = QdrantClient(QDRANT_URL)

    # Perform vector search in Qdrant
    results = client.search(
        collection_name=collection_name,
        query_vector=[0.5] * 768,  # Placeholder for actual vector encoding
        limit=top_k
    )

    # Extract and return top retrieved answers
    retrieved_answers = [doc["payload"].get("answer", "No relevant information found.") for doc in results]

    return retrieved_answers


def extract_text_from_document(document_url)  
# Uses GenAI Vision API to extract text from uploaded documents.


def extract_specific_field_from_text(text, field_name)  
# Extracts specific fields (e.g., name, address) from document text using GenAI.


def summarize_document(text)  
# Summarizes the extracted document text using GenAI.
