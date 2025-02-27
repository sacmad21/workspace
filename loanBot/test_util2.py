import pytest
import logging
import re
from unittest.mock import patch, MagicMock
from util import (
    validate_parameters,
    send_whatsapp_message,
    upload_document_to_blob,
    format_response_message
)

# ===========================
# 🔹 Mock Data for Testing
# ===========================

VALID_PARAMS = {
    "income": "50000",
    "employment_type": "Salaried",
    "aadhaar_number": "234567890123",
    "pan_number": "ABCDE1234F"
}

INVALID_PARAMS = {
    "income": "fifty thousand",
    "employment_type": "Freelancer",
    "aadhaar_number": "123456",
    "pan_number": "12345ABCDE"
}

STATE_CONFIG = {
    "income": {
        "required": True,
        "validation": {
            "regex": "^[0-9]+(\\.[0-9]{1,2})?$",
            "error_message": "❌ Income must be a valid number (e.g., 50000 or 50000.50)."
        }
    },
    "employment_type": {
        "required": True,
        "validation": {
            "regex": "^(Salaried|Self-Employed)$",
            "error_message": "❌ Employment type must be 'Salaried' or 'Self-Employed'."
        }
    },
    "aadhaar_number": {
        "required": True,
        "validation": {
            "regex": "^[2-9]{1}[0-9]{11}$",
            "error_message": "❌ Aadhaar number must be a 12-digit valid number."
        }
    },
    "pan_number": {
        "required": True,
        "validation": {
            "regex": "^[A-Z]{5}[0-9]{4}[A-Z]{1}$",
            "error_message": "❌ PAN number must be in format ABCDE1234F."
        }
    }
}

# ===========================
# 🔹 Test: validate_parameters function (5 Scenarios)
# ===========================

@pytest.mark.parametrize("test_input, expected_valid, expected_errors", [
    (VALID_PARAMS, True, 0),  # ✅ All valid inputs
    (INVALID_PARAMS, False, 4),  # ❌ All invalid inputs
    ({"income": "60000", "employment_type": "Self-Employed"}, True, 0),  # ✅ Partial valid
    ({"income": "abc123"}, False, 1),  # ❌ Invalid number format
    ({}, False, 4)  # ❌ Missing all required fields
])
def test_validate_parameters(test_input, expected_valid, expected_errors):
    valid_data, errors = validate_parameters(test_input, STATE_CONFIG)
    assert (len(errors) == 0) == expected_valid
    assert len(errors) == expected_errors
    logging.info("✅ Passed: validate_parameters")

# ===========================
# 🔹 Test: send_whatsapp_message function (5 Scenarios)
# ===========================

@patch("requests.post")
@pytest.mark.parametrize("phone_number, message, expected_status", [
    ("+919876543210", "Hello!", 200),  # ✅ Standard message
    ("+919876543210", "", 400),  # ❌ Empty message
    ("", "Test Message", 400),  # ❌ Empty phone number
    ("+919876543210", "😊🚀🔥", 200),  # ✅ Emojis
    ("+919876543210", "A" * 5000, 400),  # ❌ Exceeding message length
])
def test_send_whatsapp_message(mock_post, phone_number, message, expected_status):
    mock_post.return_value.status_code = expected_status
    send_whatsapp_message(phone_number, message)
    assert mock_post.called
    logging.info("✅ Passed: send_whatsapp_message")

# ===========================
# 🔹 Test: upload_document_to_blob function (5 Scenarios)
# ===========================

@patch("util.BlobServiceClient")
@pytest.mark.parametrize("document, expected_success", [
    ({"filename": "test.pdf", "content": b"Sample data"}, True),  # ✅ Valid PDF
    ({"filename": "image.jpg", "content": b"Binary image"}, True),  # ✅ Valid image
    ({"filename": "empty.txt", "content": b""}, False),  # ❌ Empty content
    ({"filename": "", "content": b"Data"}, False),  # ❌ Empty filename
    (None, False),  # ❌ Null input
])
def test_upload_document_to_blob(mock_blob_service, document, expected_success):
    mock_container_client = MagicMock()
    mock_blob_client = MagicMock()
    mock_blob_service.from_connection_string.return_value.get_container_client.return_value = mock_container_client
    mock_container_client.get_blob_client.return_value = mock_blob_client

    file_url = upload_document_to_blob(document) if document else None
    assert (file_url is not None) == expected_success
    logging.info("✅ Passed: upload_document_to_blob")

# ===========================
# 🔹 Test: format_response_message function (5 Scenarios)
# ===========================

@pytest.mark.parametrize("data, expected_output", [
    ({"name": "John", "age": 30}, "✅ name: John\n✅ age: 30"),  # ✅ Multiple fields
    ({"city": "New York"}, "✅ city: New York"),  # ✅ Single field
    ({}, ""),  # ❌ Empty dictionary
    ({"key": ""}, "✅ key: "),  # ✅ Empty value case
    ({"special_chars": "🔥🚀"}, "✅ special_chars: 🔥🚀")  # ✅ Emojis
])
def test_format_response_message(data, expected_output):
    formatted_message = format_response_message(data)
    assert formatted_message == expected_output
    logging.info("✅ Passed: format_response_message")

