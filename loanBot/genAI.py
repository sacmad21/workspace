import os
import logging
import requests
import traceback
import json
from dotenv import load_dotenv
from qdrant_client import QdrantClient
import openai
import logging
import traceback
import os
from extract_pdf import * 
from rag_pipeline import *

# Load environment variables
load_dotenv()

# Initialize Logger
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO if os.getenv("DEBUG_MODE", "false").lower() == "true" else logging.INFO
)

# GenAI API Configuration


GENAI_MODEL = os.getenv("GENAI_MODEL")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
GENAI_TEXT_API_URL = os.getenv("GENAI_TEXT_API_URL")


GENAI_VISION_MODEL = os.getenv("GENAI_VISION_MODEL")

GENAI_VISION_API_KEY = os.getenv("GENAI_API_KEY")


GENAI_VISION_API_URL = os.getenv("GENAI_VISION_API_URL")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_COLLECTION_LOAN = os.getenv("QDRANT_COLLECTION_LOAN")



# ===========================
# 🔹 Function: Extract Text from Document
# Load schema dynamically
with open("loanBot/propertyConfig.json", "r") as f:
    PROPERTY_SCHEMA = json.load(f)


# ===========================
# 🔹 Utility Function: Call GenAI API
# ===========================

def call_genai_api(prompt, max_tokens=150):
    """
    Calls the Together AI GenAI API to generate responses based on a prompt.
    Returns the extracted response text.
    """
    try:
        logging.info(f"\U0001F4E2 Calling GenAI API with prompt: {prompt}")


        client = openai.OpenAI(api_key=GENAI_API_KEY, base_url= "https://api.together.xyz")
        
        response = client.completions.create(
            model=GENAI_MODEL,
            prompt = prompt,
            max_tokens=max_tokens
            
        )

        result = response.choices[0].text.strip()


        logging.info(f"✅ GenAI response: {result}")
        return result
    
    except Exception as e:
        logging.error(f"❌ Exception in call_genai_api: {str(e)}")
        logging.error(traceback.format_exc())
        return None



def extract_parameters_from_document(document_url, parameters):
    """
    Uses GenAI Vision API to extract relevant fields from a document.
    """
#   parameters = STATE_CONFIG.get(state_name, {}).get("parameters", {}).keys()
#    prompt = f"Extract the following details from the uploaded document: {', '.join(parameters)} ."

    prompt = f"Extract listed parameters from given document url. \nParameters: {', '.join(parameters)} ::::\nDocument URL:: {document_url}"

    print("Prompt ::", prompt)
    headers = {
        "Authorization": f"Bearer {GENAI_VISION_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model":GENAI_VISION_MODEL,
        "document_url": document_url,
        "prompt": prompt,
        "max_tokens": 100
    }
    responseRaw = requests.post(GENAI_VISION_API_URL, headers=headers, json=data)

    print("Response :: ", responseRaw )

    response = responseRaw.json()
    try:
        extracted_data = response.get("text", "{}")
        logging.info("Extracted contents ::")
        logging.info(extracted_data)

        return eval(extracted_data)
    except Exception as e:
        print(f"Error parsing GenAI Vision response: {e}")
        return {}




# document_url, parameters = "https://api.sci.gov.in/supremecourt/2023/3848/3848_2023_8_1501_58087_Judgement_19-Dec-2024.pdf", ["PETITIONER", "RESPONDENT"]   # ✅ Standard case
# result = extract_parameters_from_document(document_url, parameters)




def extract_parameters_from_text(user_message, parameters):
    """
    Uses GenAI NLP to extract relevant parameters from user text.
    """
    print("Extract Parameters - started",user_message, parameters)

    # parameters = STATE_CONFIG.get(state_name, {}).get("parameters", {}).keys()

    prompt = f"Extract the following fields: {', '.join(parameters)}\nfrom user message :\n{user_message}"
    print("Prompt::", prompt)
    url = GENAI_TEXT_API_URL
    headers = {"Authorization": f"Bearer {GENAI_API_KEY}", "Content-Type": "application/json"}
    data = {"prompt": prompt, "max_tokens": 100 , "model":GENAI_MODEL}

    rawresponse = requests.post(url, headers=headers, json=data)

    
    response = rawresponse.json()
    print("GPT Response::", response)    


    try:
        extracted_data = response.get("text", "{}")
        print("Extract Parameters - end",eval(extracted_data))

        return eval(extracted_data)  # Convert JSON string to dictionary
    except Exception as e:
        print(f"Error parsing GenAI NLP response: {e}")
        return {}


# extract_parameters_from_text("My name is John and I live in Mumbai", ["name", "location"])



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

    url = GENAI_TEXT_API_URL
    headers = {"Authorization": f"Bearer {GENAI_API_KEY}", "Content-Type": "application/json"}
    data = {"prompt": prompt, "max_tokens": 150,  "model":GENAI_MODEL}

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
    user_id = "919819436007"
    
    retrieved_answers = answerInSpecific(user_input=query, session_id=user_id, collection=collection_name)

    return retrieved_answers




# ===========================
# 🔹 Function: Extract Text from Document
# ===========================
def extract_text_from_document(document_url):
    """
    Extracts text from an uploaded document using GenAI Vision API.
    Returns extracted text as a string or `None` if extraction fails.
    """
    try:
        logging.info(f"📢 Extracting text from document: {document_url}")

        text = extract_text_from_pdf_url(document_url)      
        
        return text 

    except Exception as e:
        logging.error(f"❌ Exception in extract_text_from_document: {str(e)}")
        logging.error(traceback.format_exc())
        return None

# rrr = extract_text_from_document("https://api.sci.gov.in/supremecourt/2019/41310/41310_2019_7_1505_53544_Judgement_10-Jul-2024.pdf")
# logging.info("TEXT::::::::::::::::::::::::" +  rrr)


# ===========================
# 🔹 Function: Extract Specific Field from Text
# ===========================

def extract_specific_field_from_text(text, field_name):
    """
    Extracts a specific field (like name, DOB, or address) from document text using GenAI.
    Returns the extracted value.
    """
    try:
        logging.info(f"📢 Extracting '{field_name}' from document text.")

        prompt = f"Extract the '{field_name}' from the following document text:\n{text}"

        headers = {
            "Authorization": f"Bearer {GENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"prompt": prompt, "max_tokens": 50 , "model":GENAI_MODEL }
        response = requests.post(GENAI_TEXT_API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            extracted_value = response.json().get("text", "").strip()
            logging.info(f"✅ Extracted '{field_name}': {extracted_value}")
            return extracted_value if extracted_value else None

        else:
            logging.error(f"❌ Field extraction failed: {response.status_code}, {response.text}")
            return None

    except Exception as e:
        logging.error(f"❌ Exception in extract_specific_field_from_text: {str(e)}")
        logging.error(traceback.format_exc())
        return None


# result = call_genai_api("Generate a summary", 100)



# ===========================
# 🔹 Function: Summarize Document
# ===========================

def summarize_document(text):
    """
    Summarizes the extracted document text using GenAI.
    Returns a concise summary.
    """
    try:
        logging.info("📢 Generating document summary.")

        prompt = f"Summarize the following document:\n{text}"

        headers = {
            "Authorization": f"Bearer {GENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"prompt": prompt, "max_tokens": 100 , "model":GENAI_MODEL}
        response = requests.post(GENAI_TEXT_API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            summary = response.json().get("text", "").strip()
            logging.info(f"✅ Document summary generated: {summary}")
            return summary if summary else "Summary not available."

        else:
            logging.error(f"❌ Document summarization failed: {response.status_code}, {response.text}")
            return "Summary not available."

    except Exception as e:
        logging.error(f"❌ Exception in summarize_document: {str(e)}")
        logging.error(traceback.format_exc())
        return "Summary not available."



def extract_specific_field_from_text(text, field_name):
    """
    Extracts a specific field (e.g., Name, Address, DOB) from document text using GenAI.
    Uses an LLM-based approach to find structured data in unstructured text.

    Parameters:
    - text (str): The raw text extracted from the document.
    - field_name (str): The field to extract (e.g., "name", "address", "date of birth").

    Returns:
    - str: Extracted field value, or None if extraction fails.
    """
    try:
        logging.info(f"📢 Extracting '{field_name}' from document text.")

        # Define structured prompt for GenAI
        prompt = f"""
        Extract the '{field_name}' from the following document text.
        If the field is not found, return 'Not Found'.
        Return only the extracted value, nothing else.

        Document Text:
        {text}
        """

        headers = {
            "Authorization": f"Bearer {GENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"prompt": prompt, "max_tokens": 50, "model":GENAI_MODEL}

        response = requests.post(GENAI_TEXT_API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            extracted_value = response.json().get("text", "").strip()

            if extracted_value.lower() == "not found":
                logging.warning(f"⚠️ '{field_name}' not found in document.")
                return None

            logging.info(f"✅ Extracted '{field_name}': {extracted_value}")
            return extracted_value

        else:
            logging.error(f"❌ Field extraction failed: {response.status_code}, {response.text}")
            return None

    except Exception as e:
        logging.error(f"❌ Exception in extract_specific_field_from_text: {str(e)}")
        logging.error(traceback.format_exc())
        return None
    


# result = generate_rag_response("What is the date of completion ?", QDRANT_COLLECTION_LOAN, 1)
# print("Rag response")
# print(result) 