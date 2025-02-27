import pytest
import logging
import json
from unittest.mock import patch, MagicMock
from genAI import (
    call_genai_api,
    extract_parameters_from_document2,
    extract_parameters_from_text,
    extract_query_parameters,
    generate_rag_response,
    extract_text_from_document,
    extract_specific_field_from_text,
    summarize_document
)

# ===========================
# 🔹 Test: call_genai_api function (5 Scenarios)
# ===========================

@patch("requests.post")
@pytest.mark.parametrize("prompt, max_tokens, mock_response, expected_output", [
    ("Generate a summary", 100, {"text": "This is a summary."}, "This is a summary."),  # ✅ Standard response
    ("", 100, {"text": ""}, ""),  # ❌ Empty response
    ("Extract data", 50, None, None),  # ❌ API failure (None)
    ("Invalid Prompt", 50, {"error": "Invalid input"}, None),  # ❌ Error response
    ("Generate a title", 50, {"text": "AI Title"}, "AI Title"),  # ✅ Valid Response
])
def test_call_genai_api(mock_post, prompt, max_tokens, mock_response, expected_output):
    mock_post.return_value.status_code = 200 if mock_response else 500
    mock_post.return_value.json.return_value = mock_response if mock_response else {}

    result = call_genai_api(prompt, max_tokens)
    assert result == expected_output
    logging.info("✅ Passed: call_genai_api")

# ===========================
# 🔹 Test: extract_parameters_from_document2 function (5 Scenarios)
# ===========================

@patch("requests.post")
@pytest.mark.parametrize("document_url, parameters, mock_response, expected_output", [
    ("http://doc.com/sample.pdf", ["name", "DOB"], '{"text": "{\\"name\\": \\"John Doe\\", \\"DOB\\": \\"01-01-1990\\"}"}', {"name": "John Doe", "DOB": "01-01-1990"}),  # ✅ Standard extraction
    ("", ["name"], '{"text": "{}"}', {}),  # ❌ Empty document
    ("http://doc.com/sample.pdf", ["address"], '{"text": "{\\"address\\": \\"New York\\"}"}', {"address": "New York"}),  # ✅ Address Extraction
    ("http://doc.com/sample.pdf", ["name"], None, {}),  # ❌ API failure
    ("http://doc.com/sample.pdf", ["unknown_field"], '{"text": "{}"}', {}),  # ❌ No fields found
])
def test_extract_parameters_from_document2(mock_post, document_url, parameters, mock_response, expected_output):
    mock_post.return_value.status_code = 200 if mock_response else 500
    mock_post.return_value.json.return_value = json.loads(mock_response) if mock_response else {}

    result = extract_parameters_from_document2(document_url, parameters)
    assert result == expected_output
    logging.info("✅ Passed: extract_parameters_from_document2")

# ===========================
# 🔹 Test: extract_query_parameters function (5 Scenarios)
# ===========================

@patch("requests.post")
@pytest.mark.parametrize("user_message, cosmos_config, mock_response, expected_output", [
    ("Find 2BHK flats", {}, '{"text": "{\\"bhk\\": 2}"}', {"bhk": 2}),  # ✅ Valid query
    ("", {}, '{"text": "{}"}', {}),  # ❌ Empty input
    ("Flats under 50L", {}, '{"text": "{\\"price\\": {\\"$lt\\": 5000000}}"}', {"price": {"$lt": 5000000}}),  # ✅ Numeric filter
    ("Tallest floor available", {}, '{"text": "{\\"complex_query\\": true}"}', {"complex_query": True}),  # ✅ Complex query
    ("Invalid query", {}, '{"text": "{}"}', {}),  # ❌ No match
])
def test_extract_query_parameters(mock_post, user_message, cosmos_config, mock_response, expected_output):
    mock_post.return_value.status_code = 200 if mock_response else 500
    mock_post.return_value.json.return_value = json.loads(mock_response) if mock_response else {}

    result = extract_query_parameters(user_message, cosmos_config)
    assert result == expected_output
    logging.info("✅ Passed: extract_query_parameters")

# ===========================
# 🔹 Test: generate_rag_response function (5 Scenarios)
# ===========================

@patch("genAI.QdrantClient.search")
@pytest.mark.parametrize("query, collection_name, top_k, mock_response, expected_output", [
    ("Tell me about loans", "LoanQA", 1, [{"payload": {"answer": "Loans are available."}}], ["Loans are available."]),  # ✅ Valid response
    ("", "LoanQA", 1, [], ["No relevant information found."]),  # ❌ No results found
    ("Complex Query", "LoanQA", 2, [{"payload": {"answer": "Complex answer"}}], ["Complex answer"]),  # ✅ Multiple top_k
    ("Invalid", "LoanQA", 1, None, ["No relevant information found."]),  # ❌ API Failure
    ("What is EMI?", "LoanQA", 1, [{"payload": {"answer": "EMI is monthly payment."}}], ["EMI is monthly payment."]),  # ✅ Valid
])
def test_generate_rag_response(mock_search, query, collection_name, top_k, mock_response, expected_output):
    mock_search.return_value = mock_response if mock_response is not None else []

    result = generate_rag_response(query, collection_name, top_k)
    assert result == expected_output
    logging.info("✅ Passed: generate_rag_response")

# ===========================
# 🔹 Test: extract_text_from_document function (5 Scenarios)
# ===========================

@patch("requests.post")
@pytest.mark.parametrize("document_url, mock_response, expected_output", [
    ("http://doc.com/sample.pdf", {"text": "Extracted document text"}, "Extracted document text"),  # ✅ Standard case
    ("", {"text": ""}, ""),  # ❌ Empty document
    ("http://doc.com/sample.pdf", None, None),  # ❌ API failure
    ("Invalid URL", {"error": "File not found"}, None),  # ❌ File not found
    ("http://doc.com/sample.pdf", {"text": "Confidential content"}, "Confidential content"),  # ✅ Valid extraction
])
def test_extract_text_from_document(mock_post, document_url, mock_response, expected_output):
    mock_post.return_value.status_code = 200 if mock_response else 500
    mock_post.return_value.json.return_value = mock_response if mock_response else {}

    result = extract_text_from_document(document_url)
    assert result == expected_output
    logging.info("✅ Passed: extract_text_from_document")

# ===========================
# 🔹 Test: summarize_document function (5 Scenarios)
# ===========================

@patch("requests.post")
@pytest.mark.parametrize("text, mock_response, expected_output", [
    ("This is a long document text.", {"text": "Summary of document."}, "Summary of document."),  # ✅ Standard case
    ("", {"text": ""}, "Summary not available."),  # ❌ Empty text
    ("Some random text.", None, "Summary not available."),  # ❌ API failure
    ("Lorem ipsum dolor sit amet", {"text": "Short summary."}, "Short summary."),  # ✅ Short text
    ("This document contains sensitive info", {"text": "Sensitive summary"}, "Sensitive summary"),  # ✅ Valid response
])
def test_summarize_document(mock_post, text, mock_response, expected_output):
    mock_post.return_value.status_code = 200 if mock_response else 500
    mock_post.return_value.json.return_value = mock_response if mock_response else {}

    result = summarize_document(text)
    assert result == expected_output
    logging.info("✅ Passed: summarize_document")
