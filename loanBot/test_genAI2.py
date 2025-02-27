import pytest
import logging
import os
from genAI import (
    call_genai_api,
    extract_parameters_from_document,
    extract_parameters_from_text,
    extract_query_parameters,
    generate_rag_response,
    extract_text_from_document,
    extract_specific_field_from_text,
    summarize_document
)

# Load API keys from environment variables
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
GENAI_TEXT_API_URL = os.getenv("GENAI_TEXT_API_URL")
GENAI_VISION_API_URL = os.getenv("GENAI_VISION_API_URL")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_COLLECTION_LOAN = os.getenv("QDRANT_COLLECTION_LOAN")

logging.basicConfig(level=logging.INFO)



# ===========================
# 🔹 Test: call_genai_api function (5 Scenarios)
# ===========================



@pytest.mark.parametrize("prompt, max_tokens", [
    ("Generate a summary", 100),  # ✅ Standard response
    ("", 100),  # ❌ Empty prompt
    ("What is AI?", 50),  # ✅ Simple question
    ("Tell me a joke", 50),  # ✅ Fun scenario
    ("Extract name from document", 50),  # ✅ Extractive task
])
def test_call_genai_api(prompt, max_tokens):
    result = call_genai_api(prompt, max_tokens)
    assert result is not None and len(result) > 0
    logging.info(f"✅ Passed: call_genai_api | Output: {result}")



# ===========================
# 🔹 Test: extract_parameters_from_document2 function (5 Scenarios)
# ===========================

@pytest.mark.parametrize("document_url, parameters", [
    ("https://api.sci.gov.in/supremecourt/2023/3848/3848_2023_8_1501_58087_Judgement_19-Dec-2024.pdf", ["name", "DOB"]),  # ✅ Standard case
    ("", ["name"]),  # ❌ Empty document
    ("https://api.sci.gov.in/supremecourt/2023/3848/3848_2023_8_1501_58087_Judgement_19-Dec-2024.pdf", ["address"]),  # ✅ Address extraction
    ("https://api.sci.gov.in/supremecourt/2023/3848/3848_2023_8_1501_58087_Judgement_19-Dec-2024.pdf", ["unknown_field"]),  # ❌ Field not found
    ("https://api.sci.gov.in/supremecourt/2023/3848/3848_2023_8_1501_58087_Judgement_19-Dec-2024.pdf", ["ID", "Date of Issue"]),  # ✅ Multiple fields
])
def test_extract_parameters_from_document(document_url, parameters):
    result = extract_parameters_from_document(document_url, parameters)
    assert isinstance(result, dict)
    logging.info(f"✅ Passed: extract_parameters_from_document2 | Output: {result}")



# ===========================
# 🔹 Test: extract_parameters_from_text function (5 Scenarios)
# ===========================

@pytest.mark.parametrize("user_message, parameters", [
    ("My name is John and I live in Mumbai", ["name", "location"]),  # ✅ Standard case
    ("", ["name"]),  # ❌ Empty message
    ("I work as a Software Engineer", ["job_title"]),  # ✅ Extract job title
    ("Random text with no relevant information", ["name"]),  # ❌ No match
    ("I was born on 1st Jan 1990", ["DOB"]),  # ✅ Date extraction
])
def test_extract_parameters_from_text(user_message, parameters):
    result = extract_parameters_from_text(user_message, parameters)
    assert isinstance(result, dict)
    logging.info(f"✅ Passed: extract_parameters_from_text | Output: {result}")

# ===========================
# 🔹 Test: extract_query_parameters function (5 Scenarios)
# ===========================



@pytest.mark.parametrize("user_message", [
    ("Find 2BHK flats"),  # ✅ Valid query
    (""),  # ❌ Empty input
    ("Flats under 50L"),  # ✅ Numeric filter
    ("Tallest floor available"),  # ✅ Complex query
    ("Invalid query"),  # ❌ No match
])
def test_extract_query_parameters(user_message):
    result = extract_query_parameters(user_message, {})
    assert isinstance(result, dict)
    logging.info(f"✅ Passed: extract_query_parameters | Output: {result}")

# ===========================
# 🔹 Test: generate_rag_response function (5 Scenarios)
# ===========================

@pytest.mark.parametrize("query, collection_name, top_k", [
    ("What is the date of completion ?", QDRANT_COLLECTION_LOAN, 1),  # ✅ Valid response
    ("", QDRANT_COLLECTION_LOAN, 1),  # ❌ Empty query
    ("What kind of materisl are used ?", QDRANT_COLLECTION_LOAN, 2),  # ✅ Multiple top_k
    ("What are the payment options ?", QDRANT_COLLECTION_LOAN, 3),  # ✅ Complex response
    ("What is the progress ?", QDRANT_COLLECTION_LOAN, 1),  # ❌ API Failure
])
def test_generate_rag_response(query, collection_name, top_k):
    result = generate_rag_response(query, collection_name, top_k)
    assert isinstance(result, list)
    logging.info(f"✅ Passed: generate_rag_response | Output: {result}")





# ===========================
# 🔹 Test: extract_text_from_document function (5 Scenarios)
# ===========================

@pytest.mark.parametrize("document_url", [
    ("https://api.sci.gov.in/supremecourt/2023/3848/3848_2023_8_1501_58087_Judgement_19-Dec-2024.pdf"),  # ✅ Standard case
    (""),  # ❌ Empty document
    ("https://api.sci.gov.in/supremecourt/2023/3848/3848_2023_8_1501_58087_Judgement_19-Dec-2024.pdf"),  # ✅ Valid URL
    ("https://api.sci.gov.in/supremecourt/2023/3848/3848_2023_8_1501_58087_Judgement_19-Dec-2024.pdf"),  # ✅ Valid document
    ("https://api.sci.gov.in/supremecourt/2023/3848/3848_2023_8_1501_58087_Judgement_19-Dec-2024.pdf"),  # ✅ Valid case
])
def test_extract_text_from_document(document_url):
    result = extract_text_from_document(document_url)
    
    assert result is not None
    logging.info(f"✅ Passed: extract_text_from_document | Output: {result}")

# ===========================
# 🔹 Test: extract_specific_field_from_text function (5 Scenarios)
# ===========================

@pytest.mark.parametrize("text, field_name", [
    ("Name: Alice\nDOB: 01/01/1990", "name"),  # ✅ Extract name
    ("", "name"),  # ❌ Empty text
    ("ID: 1234", "phone"),  # ❌ Field not found
    ("Contact: 9876543210", "phone"),  # ✅ Extract phone
    ("Address: 123 Street", "address"),  # ✅ Extract address
])
def test_extract_specific_field_from_text(text, field_name):
    result = extract_specific_field_from_text(text, field_name)

    assert result is not None
    logging.info(f"✅ Passed: extract_specific_field_from_text | Output: {result}")

# ===========================
# 🔹 Test: summarize_document function (5 Scenarios)
# ===========================

@pytest.mark.parametrize("text", [
    ("This is a long document text."),  # ✅ Standard case
    (""),  # ❌ Empty text
    ("Some random text."),  # ✅ Short text
    ("Lorem ipsum dolor sit amet"),  # ✅ Standard case
    ("This document contains sensitive info"),  # ✅ Valid response
])
def test_summarize_document(text):
    result = summarize_document(text)
    assert result is not None
    logging.info(f"✅ Passed: summarize_document | Output: {result}")

