import re

from formFillingBot.util import validation_rules 
from formFillingBot.util import workflow_steps

def validate_field(step, field, value):
    """Validate an individual field based on predefined rules."""
    step_rules = validation_rules.get(step, {})
    patterns = step_rules.get("patterns", {})

    # Check if the field has a pattern
    if field in patterns:
        pattern = patterns[field]
        check = bool(re.match(pattern, str(value) ))
        print( f"""Validation Regex Pattern::{pattern}::  Data:::{value}:::  Check:::{check}::: """  )

        return check

    return True  # If no pattern is defined, assume valid


def validate_step(data, current_step):
    """Validate the data for a specific step."""
    step_rules = validation_rules.get(current_step, {})
    required_fields = step_rules.get("fields", [])

    print(" Validation complete Step :Data", data)

    # Check all required fields
    for field in required_fields:
        if field not in data :
            print( f"""Validation failed: No :::{field}::: not in data :::{data[field]}:::""" )
            return False  # Missing or empty field

        # Validate field value
        if not validate_field(current_step, field, data[field]):
            print( f"""Validation Failed :{field}:  invalid data :{data[field]}""" )
            return False

        print (f"""Valid::{field}: for data :{data[field]}:""")
        
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

    for step in workflow_steps:
        if not validate_step(data, step):
            return False  # Validation failed for a step

    return True
