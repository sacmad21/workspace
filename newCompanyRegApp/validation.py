import re

# Validation rules for each step
validation_rules = {
    "eligibility_check": {
        "questions": 5,
        "valid_responses": ["Yes", "No"]
    },
    "basic_details": {
        "fields": ["fullName","fatherOrGuardianName","DOB","aadharNumber","mobileNumber","address"],
        "patterns": {
            "Date of Birth": r"^\d{2}/\d{2}/\d{4}$",  # DD/MM/YYYY
            "Aadhaar Number": r"^\d{12}$",
            "Mobile Number": r"^\d{10}$"
        }
    },
    "bank_details": {
        "fields": ["bankName","branchName","accountHolderName","accountNumber","ifscCode"],
        "patterns": {
            "Account Number": r"^\d{9,18}$",
            "IFSC Code": r"^[A-Z]{4}0[A-Z0-9]{6}$"
        }
    },
    "educational_details": {
        "fields": ["nameOfInstution","yearOfPassingClass10","marksOntainedIn10Class","valid10ClassCertificate"],
        "patterns": {
            "Year of Passing Class 10": r"^\d{4}$",
            "Marks Obtained in Class 10": r"^\d{1,3}$"
        }
    },
    "family_income": {
        "fields": ["annualFamilyIncome","sourceOfIncome","doHaveBplCard"],
        "patterns": {
            "Total Annual Family Income": r"^\d+(\.\d{1,2})?$"  # Valid number format
        }
    }
}


def validate_field(step, field, value):
    """Validate an individual field based on predefined rules."""
    step_rules = validation_rules.get(step, {})
    patterns = step_rules.get("patterns", {})

    # Check if the field has a pattern
    if field in patterns:
        pattern = patterns[field]
        return bool(re.match(pattern, value))

    return True  # If no pattern is defined, assume valid


def validate_step(data, current_step):
    """Validate the data for a specific step."""
    step_rules = validation_rules.get(current_step, {})
    required_fields = step_rules.get("fields", [])

    # Check all required fields
    for field in required_fields:
        if field not in data or not data[field]:
            print("Validation failed: No ", field , " not in data :", data[field] )
            return False  # Missing or empty field

        # Validate field value
        if not validate_field(current_step, field, data[field]):
            print("Validation Failed :", field , " invalid data :", data[field] )
            return False

    return True


def validate_final_form(data):
    """Validate the entire form before submission."""
    mandatory_steps = [
        "eligibility_check",
        "basic_details",
        "bank_details",
        "educational_details",
        "family_income"
    ]

    for step in mandatory_steps:
        if not validate_step(data, step):
            return False  # Validation failed for a step

    return True
