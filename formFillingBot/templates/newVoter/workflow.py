# workflow.py

# Workflow Steps
form_workflow_steps = [
    "welcome",
    "personal_details",
    "relative_details",
    "contact_details",
    "aadhaar_details",
    "address_details",
    "disability",
    "family_reference",
    "declaration"
]

# Mandatory Documents
form_mandatory_documents = []

# Workflow Prompts
form_prompts = {
    "welcome": "Welcome to the New Voter Registration Assistant! Let's check your eligibility to apply for a new Voter ID. Please answer the following questions:\n1. Are you an Indian citizen? (Yes/No)\n2. Are you at least 18 years old as of January 1st of this year? (Yes/No)\n3. Are you applying for the first time for voter registration? (Yes/No)\n4. Do you currently live at your present address for at least 6 months? (Yes/No)\n5. Do you have valid documents for age and address proof? (Yes/No)",
    "personal_details": "Please provide your personal details:\n1. Full Name (in official language):\n2. Full Name (in English BLOCK LETTERS):\n3. Gender (Male/Female/Third Gender):\n4. Date of Birth (DD-MM-YYYY):\n5. Upload age proof document:\n6. Upload passport size photo (4.5 cm x 3.5 cm):",
    "relative_details": "Please provide a relative's details:\n1. Relation Type (Father/Mother/Husband/Wife/Guardian/Guru):\n2. Full Name (in official language):\n3. Full Name (in English BLOCK LETTERS):",
    "contact_details": "Contact Details:\n1. Mobile Number:\n2. Email ID (if available):",
    "aadhaar_details": "Aadhaar Details:\nDo you have Aadhaar? (Yes/No)\nIf Yes, enter Aadhaar Number:",
    "address_details": "Present Address Details:\n1. House/Building/Apartment No.:\n2. Street/Area/Mohalla:\n3. Town/Village:\n4. Post Office:\n5. PIN Code:\n6. Tehsil/Taluqa/Mandal:\n7. District:\n8. State/UT:\n9. Since when are you residing here? (MM-YYYY):\n10. Upload address proof:",
    "disability": "Disability Information (Optional):\n1. Do you have any disability? (Yes/No)\nIf Yes:\n2. Type of Disability:\n3. Percentage of Disability:\n4. Upload Certificate:",
    "family_reference": "Details of a family member already registered at the same address:\n1. Name of family member:\n2. Relationship:\n3. EPIC (Voter ID) Number:",
    "declaration": "Declaration:\n1. Place of Birth (Village/Town, District, State/UT):\n2. Are you applying for the first time in any constituency? (Yes/No)\nType 'YES' to agree:\n'I declare that the information provided is true to the best of my knowledge. I understand that any false information may lead to rejection under the Representation of the People Act, 1950.'"
}

# Workflow Fields
form_fields = {
    "welcome": [
        "isIndianCitizen",
        "is18YearsOld",
        "isFirstTimeApplicant",
        "isResidentSince6Months",
        "hasValidDocs"
    ],
    "personal_details": [
        "nameLocalLang",
        "nameEnglish",
        "gender",
        "dob",
        "ageProofUpload",
        "passportPhotoUpload"
    ],
    "relative_details": [
        "relationType",
        "relativeNameLocalLang",
        "relativeNameEnglish"
    ],
    "contact_details": [
        "mobileNumber",
        "email"
    ],
    "aadhaar_details": [
        "hasAadhaar",
        "aadhaarNumber"
    ],
    "address_details": [
        "houseNumber",
        "streetArea",
        "townVillage",
        "postOffice",
        "pinCode",
        "tehsil",
        "district",
        "state",
        "residenceSince",
        "addressProofUpload"
    ],
    "disability": [
        "hasDisability",
        "disabilityType",
        "disabilityPercentage",
        "disabilityCertificate"
    ],
    "family_reference": [
        "familyMemberName",
        "familyRelationship",
        "familyEpicNumber"
    ],
    "declaration": [
        "placeOfBirth",
        "isFirstTimeVoter",
        "formDeclaration"
    ]
}

# Validation Rules
form_validation_rules = {
    "welcome": {
        "questions": 5,
        "fields": [
            "isIndianCitizen",
            "is18YearsOld",
            "isFirstTimeApplicant",
            "isResidentSince6Months",
            "hasValidDocs"
        ],
        "valid_responses": [
            "Yes",
            "No"
        ],
        "patterns": {},
        "confirmation": True
    },
    "personal_details": {
        "questions": 0,
        "fields": [
            "nameLocalLang",
            "nameEnglish",
            "gender",
            "dob",
            "ageProofUpload",
            "passportPhotoUpload"
        ],
        "valid_responses": [],
        "patterns": {
            "dob": "^\\d{2}-\\d{2}-\\d{4}$"
        },
        "confirmation": True
    },
    "relative_details": {
        "questions": 0,
        "fields": [
            "relationType",
            "relativeNameLocalLang",
            "relativeNameEnglish"
        ],
        "valid_responses": [],
        "patterns": {},
        "confirmation": True
    },
    "contact_details": {
        "questions": 0,
        "fields": [
            "mobileNumber",
            "email"
        ],
        "valid_responses": [],
        "patterns": {
            "mobileNumber": "^\\d{10}$"
        },
        "confirmation": True
    },
    "aadhaar_details": {
        "questions": 0,
        "fields": [
            "hasAadhaar",
            "aadhaarNumber"
        ],
        "valid_responses": [],
        "patterns": {
            "aadhaarNumber": "^\\d{12}$"
        },
        "confirmation": True
    },
    "address_details": {
        "questions": 0,
        "fields": [
            "houseNumber",
            "streetArea",
            "townVillage",
            "postOffice",
            "pinCode",
            "tehsil",
            "district",
            "state",
            "residenceSince",
            "addressProofUpload"
        ],
        "valid_responses": [],
        "patterns": {
            "pinCode": "^\\d{6}$",
            "residenceSince": "^\\d{2}-\\d{4}$"
        },
        "confirmation": True
    },
    "disability": {
        "questions": 0,
        "fields": [
            "hasDisability",
            "disabilityType",
            "disabilityPercentage",
            "disabilityCertificate"
        ],
        "valid_responses": [],
        "patterns": {},
        "confirmation": True
    },
    "family_reference": {
        "questions": 0,
        "fields": [
            "familyMemberName",
            "familyRelationship",
            "familyEpicNumber"
        ],
        "valid_responses": [],
        "patterns": {},
        "confirmation": True
    },
    "declaration": {
        "questions": 0,
        "fields": [
            "placeOfBirth",
            "isFirstTimeVoter",
            "formDeclaration"
        ],
        "valid_responses": [],
        "patterns": {},
        "confirmation": True
    }
}

if __name__ == '__main__':
    print("Voter Form Filled up Successfully!")
