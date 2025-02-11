from util import send_whatsapp_message
from state_manager import STATE_CONFIG
from mongo_util import construct_mongo_query
from genAI import extract_query_parameters
import pymongo
import json
import requests
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
COSMOS_CONNECTION_STRING = os.getenv("COSMOS_CONNECTION_STRING")

# Initialize MongoDB Client
mongo_client = pymongo.MongoClient(COSMOS_CONNECTION_STRING)
# Load the schema dynamically from `propertyConfig.json`
with open("propertyConfig.json", "r") as f:
    PROPERTY_SCHEMA = json.load(f)



def construct_mongo_query(extracted_params):
    """
    Constructs a MongoDB query dynamically based on extracted parameters.
    Uses GenAI if complex query logic is needed.
    """

    # Basic Mongo query structure
    mongo_query = {}

    # Direct field matches
    if "society_name" in extracted_params:
        mongo_query["society_name"] = extracted_params["society_name"]

    if "location.city" in extracted_params:
        mongo_query["location.city"] = extracted_params["location.city"]

    if "property_type" in extracted_params:
        mongo_query["property_variants.configuration_name"] = extracted_params["property_type"]

    if "bhk" in extracted_params:
        mongo_query["property_variants.bhk"] = int(extracted_params["bhk"])

    if "facing" in extracted_params:
        mongo_query["property_variants.facing"] = extracted_params["facing"]

    if "price" in extracted_params:
        if "price_operator" in extracted_params:  # Supports 'greater than' or 'less than' conditions
            operator = extracted_params["price_operator"]
            if operator == "above":
                mongo_query["property_variants.price"] = {"$gt": int(extracted_params["price"])}
            elif operator == "below":
                mongo_query["property_variants.price"] = {"$lt": int(extracted_params["price"])}
        else:
            mongo_query["property_variants.price"] = int(extracted_params["price"])

    if "floor" in extracted_params:
        if "floor_operator" in extracted_params:
            operator = extracted_params["floor_operator"]
            if operator == "above":
                mongo_query["property_variants.wings"] = {"$elemMatch": {"$gt": int(extracted_params["floor"])}}
            elif operator == "below":
                mongo_query["property_variants.wings"] = {"$elemMatch": {"$lt": int(extracted_params["floor"])}}
        else:
            mongo_query["property_variants.wings"] = extracted_params["floor"]

    if "room_sizes.hall" in extracted_params:
        mongo_query["property_variants.room_sizes.hall"] = {"$gt": int(extracted_params["room_sizes.hall"])}

    if "club_amenities" in extracted_params:
        mongo_query[f"club_amenities.{extracted_params['club_amenities']}"] = {"$exists": True}

    if "amenities" in extracted_params:
        mongo_query[f"open_amenities.{extracted_params['amenities']}"] = {"$exists": True}

    # If a complex query is needed, generate via GenAI
    if "complex_query" in extracted_params:
        genai_mongo_query = generate_mongo_query_from_genai(extracted_params["complex_query"])
        if genai_mongo_query:
            mongo_query.update(genai_mongo_query)

    return mongo_query



def generate_mongo_query_from_genai(user_query):
    """
    Uses GenAI to generate a MongoDB query for complex user requests.
    """

    schema_description = json.dumps(PROPERTY_SCHEMA, indent=2)

    prompt = f"""
    Convert the following user query into a MongoDB query:

    Schema:
    {schema_description}

    User Query: "{user_query}"

    Generate a MongoDB query in JSON format:
    """

    url = "https://api.together.xyz/generate"
    headers = {"Authorization": f"Bearer {TOGETHER_GENAI_API_KEY}", "Content-Type": "application/json"}
    data = {"prompt": prompt, "max_tokens": 200}

    response = requests.post(url, headers=headers, json=data).json()

    try:
        extracted_data = response.get("text", "{}")
        return json.loads(extracted_data)  # Convert JSON string to dictionary
    except Exception as e:
        print(f"Error parsing GenAI response: {e}")
        return {}

def fetch_documents_from_mongo(db_name, collection_name, query):
    """
    Fetches matching documents from Azure Cosmos DB (Mongo API).
    """

    db = mongo_client[db_name]
    collection = db[collection_name]

    # Retrieve matching documents
    results = collection.find(query, {"_id": 0}).limit(3)  # Limit results for RAG processing
    return list(results)