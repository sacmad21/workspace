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
# 🔹 Test: validate_parameters function
# ===========================

def test_validate_parameters():
    valid_data, errors = validate_parameters(VALID_PARAMS, STATE_CONFIG)
    assert "income" in valid_data
    assert "employment_type" in valid_data
    assert "aadhaar_number" in valid_data
    assert "pan_number" in valid_data
    assert len(errors) == 0

    valid_data, errors = validate_parameters(INVALID_PARAMS, STATE_CONFIG)
    assert len(errors) > 0
    assert "income" in errors
    assert "employment_type" in errors
    assert "aadhaar_number" in errors
    assert "pan_number" in errors

    logging.info("✅ Passed: validate_parameters")

# ===========================
# 🔹 Test: send_whatsapp_message function (Mock)
# ===========================

@patch("requests.post")
def test_send_whatsapp_message(mock_post):
    mock_post.return_value.status_code = 200
    send_whatsapp_message("+919876543210", "Hello, this is a test message.")
    assert mock_post.called
    logging.info("✅ Passed: send_whatsapp_message (Mocked)")

# ===========================
# 🔹 Test: upload_document_to_blob function (Mock)
# ===========================

@patch("util.BlobServiceClient")
def test_upload_document_to_blob(mock_blob_service):
    mock_container_client = MagicMock()
    mock_blob_client = MagicMock()

    mock_blob_service.from_connection_string.return_value.get_container_client.return_value = mock_container_client
    mock_container_client.get_blob_client.return_value = mock_blob_client

    document = {
        "filename": "test.pdf",
        "content": b"Sample binary content"
    }

    file_url = upload_document_to_blob(document)
    assert file_url is not None
    logging.info("✅ Passed: upload_document_to_blob (Mocked)")

# ===========================
# 🔹 Test: format_response_message function
# ===========================

def test_format_response_message():
    data = {"name": "John Doe", "age": 30}
    formatted_message = format_response_message(data)
    assert "✅ name: John Doe" in formatted_message
    assert "✅ age: 30" in formatted_message
    logging.info("✅ Passed: format_response_message")
