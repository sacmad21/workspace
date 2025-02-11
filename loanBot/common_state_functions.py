import json
import requests
from util import send_whatsapp_message, upload_document_to_blob
from genAI import extract_text_from_document
from state_manager import STATE_CONFIG
from util import send_whatsapp_message
from state_manager import STATE_CONFIG
from mongo_util import construct_mongo_query
from genAI import extract_query_parameters
import pymongo
import os
from dotenv import load_dotenv
from util import send_whatsapp_message
from state_manager import STATE_CONFIG
from genAI import generate_rag_response



# Load environment variables
load_dotenv()
COSMOS_CONNECTION_STRING = os.getenv("COSMOS_CONNECTION_STRING")

# Initialize MongoDB Client
mongo_client = pymongo.MongoClient(COSMOS_CONNECTION_STRING)

from util import send_whatsapp_message, validate_parameters, upload_document_to_blob
from genAI import extract_parameters_from_text, extract_parameters_from_document
from state_manager import STATE_CONFIG

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "pdf"}

def collect_parameters(state_manager, phone_number, user_message=None, document=None):
    """
    Collect parameters from text message OR document based on user input.
    - If user sends text, extract parameters using GenAI NLP.
    - If user uploads a document, extract parameters using GenAI Vision.
    - If parameters are incomplete, ask the user for missing ones.
    """
    state_name = state_manager.state_name
    state_config = STATE_CONFIG.get(state_name, {})

    # Get required parameters for this state
    required_params = state_config.get("parameters", {})

    # Get current user state data
    user_data = state_manager.get_data()

    # Step 1: Extract parameters from the text message (if provided)
    if user_message:
        extracted_from_text = extract_parameters_from_text(user_message, state_name)
        user_data.update(extracted_from_text)

    # Step 2: Extract parameters from the uploaded document (if provided & allowed)
    if document:
        if state_config.get("Read_Param_From_Document", False):
            file_extension = document["filename"].split(".")[-1].lower()

            if file_extension not in ALLOWED_EXTENSIONS:
                send_whatsapp_message(phone_number, "❌ Unsupported file format. Please upload a PDF or JPG file.")
                return False  # Stop further processing

            # Upload document to Azure Blob Storage
            document_url = upload_document_to_blob(document)
            if not document_url:
                send_whatsapp_message(phone_number, "❌ Document upload failed. Please try again.")
                return False

            # Extract details from document using GenAI Vision API
            extracted_from_doc = extract_parameters_from_document(document_url, state_name)
            user_data.update(extracted_from_doc)

    # Step 3: Validate extracted parameters
    valid_params, errors = validate_parameters(user_data, state_name)

    if errors:
        for param, error in errors.items():
            send_whatsapp_message(phone_number, error)
        return False  # Stop further processing

    # Step 4: Check for missing parameters
    missing_params = [param for param in required_params if param not in valid_params]

    if missing_params:
        # Ask the user to provide missing details
        message = f"Please provide the following missing details: {', '.join(missing_params)}."
        send_whatsapp_message(phone_number, message)
        state_manager.update_state(valid_params)  # Save collected parameters
        return False  # Indicate that further input is needed

    # Step 5: Confirm extracted details with the user
    extracted_text = "\n".join([f"✅ {k}: {v}" for k, v in valid_params.items()])
    send_whatsapp_message(phone_number, f"📄 Extracted details:\n{extracted_text}\n\n✅ Confirm? Reply 'Yes' to proceed or 'No' to edit.")

    state_manager.update_state(valid_params)  # Save collected parameters
    state_manager.transition("awaiting_parameter_confirmation")

    return True  # Successfully collected parameters



def handle_rag_query(state_manager, phone_number, user_message):
    """
    Handles Q/A queries using Retrieval-Augmented Generation (RAG).
    - Uses `RetrieverDocCount` from state_config.json to fetch multiple relevant answers.
    - Continues Q/A mode until the user explicitly exits by typing 'End'.
    """

    state_name = state_manager.state_name
    state_config = STATE_CONFIG.get(state_name, {})

    # Check if Q/A is enabled in this state
    if state_config.get("Support_QA") != "RAG":
        return False  # Exit if RAG Q/A is not enabled

    # Get RAG retrieval settings
    rag_config = state_config.get("RAG", {})
    collection_name = rag_config.get("collectionName", "LoanQA")  # Default collection
    retriever_doc_count = rag_config.get("RetrieverDocCount", 1)  # Default is 1 document

    # Fetch answer(s) from Qdrant Vector DB
    retrieved_answers = generate_rag_response(user_message, collection_name, retriever_doc_count)

    # Format and send retrieved answers
    if retrieved_answers:
        response_text = "\n\n".join([f"📌 Answer {i+1}:\n{ans}" for i, ans in enumerate(retrieved_answers)])
    else:
        response_text = "I couldn't find any information related to your question."

    send_whatsapp_message(phone_number, f"{response_text}\n\nAsk more questions or type 'End' to exit Q/A mode.")

    # If user types "End", transition to the next state
    if user_message.lower() == "end":
        send_whatsapp_message(phone_number, "✅ Q/A session ended. Proceeding to the next step.")
        state_manager.transition(state_config.get("next_state", "awaiting_next_action"))
        return True

    return True  # Indicate that Q/A processing occurred







def guide_user_for_document(state_manager, phone_number):
    """
    Guides the user to upload documents based on the config.
    - Asks for the next missing document.
    - Allows skipping optional documents.
    - Ensures all mandatory documents are uploaded before proceeding.
    """

    state_name = state_manager.state_name
    state_config = STATE_CONFIG.get(state_name, {})

    if not state_config.get("UploadDocuments", False):
        return False

    # Get document configurations
    documents_config = state_config.get("DocumentsConfig", {})

    # Get current user state
    user_data = state_manager.get_data()
    uploaded_docs = user_data.get("uploaded_documents", {})

    # Identify missing documents
    missing_mandatory_docs = [
        doc for doc, config in documents_config.items()
        if config.get("required", False) and doc not in uploaded_docs
    ]

    missing_optional_docs = [
        doc for doc, config in documents_config.items()
        if not config.get("required", False) and doc not in uploaded_docs
    ]

    # If there are still mandatory documents to upload, request the next one
    if missing_mandatory_docs:
        next_doc = missing_mandatory_docs[0]
        send_whatsapp_message(phone_number, f"📃 Please upload your {next_doc}. Accepted formats: {', '.join(documents_config[next_doc]['allowed_formats'])}.")
        return

    # If mandatory documents are done, ask for optional documents one by one
    if missing_optional_docs:
        next_doc = missing_optional_docs[0]
        send_whatsapp_message(phone_number, f"📃 Would you like to upload your {next_doc}? Type 'Skip' to move to the next document.")
        return

    # If all required documents are uploaded, confirm and transition
    send_whatsapp_message(phone_number, "✅ All required documents uploaded successfully. Type 'Done' to finish.")
    return

def process_document_upload(state_manager, phone_number, document):
    """
    Handles document uploads, validation, and metadata extraction.
    Ensures all required documents are collected before proceeding.
    """

    state_name = state_manager.state_name
    state_config = STATE_CONFIG.get(state_name, {})

    if not state_config.get("UploadDocuments", False):
        send_whatsapp_message(phone_number, "❌ Document upload is not required for this step.")
        return False

    # Get document configurations
    documents_config = state_config.get("DocumentsConfig", {})

    # Extract document type from filename
    file_extension = document["filename"].split(".")[-1].lower()
    document_type = document["document_type"]  # This should be provided by the user

    if document_type not in documents_config:
        send_whatsapp_message(phone_number, f"❌ Unsupported document type: {document_type}. Please upload a valid document.")
        return False

    # Validate file format
    allowed_formats = documents_config[document_type].get("allowed_formats", [])
    if file_extension not in allowed_formats:
        send_whatsapp_message(phone_number, f"❌ Invalid file format. Allowed formats for {document_type}: {', '.join(allowed_formats)}.")
        return False

    # Upload document to Azure Blob Storage
    document_url = upload_document_to_blob(document)
    if not document_url:
        send_whatsapp_message(phone_number, "❌ Document upload failed. Please try again.")
        return False

    # Extract text and metadata from the document
    extracted_text = extract_text_from_document(document_url)

    # Perform document validation if required
    validation_field = documents_config[document_type].get("validation_field")
    compare_with = documents_config[document_type].get("compare_with")

    if validation_field and compare_with:
        user_data = state_manager.get_data()
        expected_value = user_data.get(compare_with)

        extracted_value = extract_specific_field_from_text(extracted_text, validation_field)

        if expected_value and extracted_value:
            if expected_value.lower() != extracted_value.lower():
                send_whatsapp_message(phone_number, f"⚠️ {document_type} validation failed. Extracted {validation_field} does not match user profile.")
                return False
            else:
                send_whatsapp_message(phone_number, f"✅ {document_type} validated successfully.")

    # Store uploaded document info
    if "uploaded_documents" not in user_data:
        user_data["uploaded_documents"] = {}

    user_data["uploaded_documents"][document_type] = document_url
    state_manager.update_state(user_data)

    send_whatsapp_message(phone_number, f"📤 {document_type} uploaded successfully.")
    
    # Guide the user for the next required document
    guide_user_for_document(state_manager, phone_number)
    return True


def handle_mongo_rag_query(state_manager, phone_number, user_message):
    """
    Handles Q/A queries using Azure Cosmos DB (Mongo API).
    """

    state_name = state_manager.state_name
    state_config = STATE_CONFIG.get(state_name, {})

    # Check if MONGO_RAG is enabled
    if state_config.get("Support_QA") != "MONGO_RAG":
        return False  # Exit if MONGO_RAG is not enabled

    # Get MongoDB retrieval settings
    cosmos_config = state_config.get("COSMOS_RAG", {})
    db_name = cosmos_config.get("DBName", "LoanDataDB")
    collection_name = cosmos_config.get("CollectionName", "PropertyOptions")

    # Extract query parameters using GenAI
    extracted_params = extract_query_parameters(user_message, cosmos_config)

    if not extracted_params:
        send_whatsapp_message(phone_number, "I couldn't understand your query. Please rephrase it.")
        return True

    # Generate MongoDB query
    mongo_query = construct_mongo_query(extracted_params)

    # Fetch relevant documents from MongoDB
    retrieved_documents = fetch_documents_from_mongo(db_name, collection_name, mongo_query)

    if not retrieved_documents:
        send_whatsapp_message(phone_number, "No relevant information found.")
        return True

    # Generate response using retrieved documents
    response_text = generate_rag_response(user_message, retrieved_documents)

    send_whatsapp_message(phone_number, response_text)

    if user_message.lower() == "end":
        send_whatsapp_message(phone_number, "✅ Q/A session ended. Proceeding to the next step.")
        state_manager.transition(state_config.get("next_state", "awaiting_next_action"))
        return True

    return True  # Indicate that Q/A processing occurred

def fetch_documents_from_mongo(db_name, collection_name, query):
    """
    Fetches matching documents from Azure Cosmos DB (Mongo API).
    """

    db = mongo_client[db_name]
    collection = db[collection_name]

    # Retrieve matching documents
    results = collection.find(query, {"_id": 0}).limit(3)  # Limit results for RAG processing
    return list(results)
