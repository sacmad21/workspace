# workflow.py

# Workflow Steps
form_workflow_steps = [
    "welcome",
    "eligibility_check",
    "basic_details",
    "bank_details",
    "family_income",
    "document_upload",
    "declaration"
]

# Mandatory Documents
form_mandatory_documents = [
    "isAadharUploaded",
    "isMarriageCertificateUploaded",
    "isBankPassbookUploaded",
    "isIncomeCertificateUploaded",
    "isResidentialProofUploaded"
]

# Workflow Prompts
form_prompts = {
    "welcome": "Welcome! Are you interested in applying for the Griha Aadhar Scheme in Goa? (Yes/No)",
    "eligibility_check": "Let's check your eligibility:\n1. Are you a resident of Goa? (Yes/No)\n2. Are you a married woman living in Goa? (Yes/No)\n3. Is your total family income below \u20b93,00,000 per annum? (Yes/No)\n4. Do you or your spouse already receive financial assistance from a similar scheme? (Yes/No)",
    "basic_details": "Please provide your personal details:\n1. Full Name?\n2. Husband's Name?\n3. Date of Birth (DD-MM-YYYY)?\n4. Aadhaar Number?\n5. Mobile Number?\n6. Residential Address?",
    "bank_details": "Please provide your bank account details:\n1. Account Holder's Name?\n2. Bank Name?\n3. Branch Name?\n4. Account Number?\n5. IFSC Code?",
    "family_income": "Please provide your family's income details:\n1. What is your Total Annual Family Income (in INR)?\n2. What is your Occupation/Source of Income?",
    "document_upload": "Upload the following mandatory documents one by one:\n- Aadhaar Card\n- Marriage Certificate\n- Bank Passbook Copy\n- Income Certificate\n- Residential Proof",
    "declaration": "Please confirm the following declaration:\n'I hereby declare that all the information provided is True to the best of my knowledge. Any False information may lead to rejection of my application.'\nType 'YES' to agree and complete the process."
}

# Workflow Fields
form_fields = {
    "welcome": [
        "isInterested"
    ],
    "eligibility_check": [
        "isResident_of_Goa",
        "isMarriedWomanInGoa",
        "isIncomeBelow3L",
        "isAlreadyReceivingAssistance"
    ],
    "basic_details": [
        "fullName",
        "husbandName",
        "DOB",
        "aadharNumber",
        "mobileNumber",
        "address"
    ],
    "bank_details": [
        "accountHolderName",
        "bankName",
        "branchName",
        "accountNumber",
        "ifscCode"
    ],
    "family_income": [
        "annualFamilyIncome",
        "sourceOfIncome"
    ],
    "document_upload": [
        "isAadharUploaded",
        "isMarriageCertificateUploaded",
        "isBankPassbookUploaded",
        "isIncomeCertificateUploaded",
        "isResidentialProofUploaded"
    ],
    "declaration": [
        "formDeclaration"
    ]
}

# Validation Rules
form_validation_rules = {
    "welcome": {
        "questions": 1,
        "fields": [
            "isInterested"
        ],
        "valid_responses": [
            "Yes",
            "No"
        ],
        "patterns": {},
        "confirmation": False
    },
    "eligibility_check": {
        "questions": 4,
        "fields": [
            "isResident_of_Goa",
            "isMarriedWomanInGoa",
            "isIncomeBelow3L",
            "isAlreadyReceivingAssistance"
        ],
        "valid_responses": [
            "Yes",
            "No"
        ],
        "patterns": {},
        "confirmation": True
    },
    "basic_details": {
        "questions": 0,
        "fields": [
            "fullName",
            "husbandName",
            "DOB",
            "aadharNumber",
            "mobileNumber",
            "address"
        ],
        "valid_responses": [],
        "patterns": {
            "DOB": "^\\d{2}-\\d{2}-\\d{4}$",
            "aadharNumber": "^\\d{12}$",
            "mobileNumber": "^\\d{10}$"
        },
        "confirmation": True
    },
    "bank_details": {
        "questions": 0,
        "fields": [
            "accountHolderName",
            "bankName",
            "branchName",
            "accountNumber",
            "ifscCode"
        ],
        "valid_responses": [],
        "patterns": {
            "ifscCode": "^[A-Z]{4}0[A-Z0-9]{6}$"
        },
        "confirmation": True
    },
    "family_income": {
        "questions": 0,
        "fields": [
            "annualFamilyIncome",
            "sourceOfIncome"
        ],
        "valid_responses": [],
        "patterns": {
            "annualFamilyIncome": "^\\d+(\\.\\d{1,2})?$"
        },
        "confirmation": True
    },
    "document_upload": {
        "questions": 0,
        "fields": [
            "isAadharUploaded",
            "isMarriageCertificateUploaded",
            "isBankPassbookUploaded",
            "isIncomeCertificateUploaded",
            "isResidentialProofUploaded"
        ],
        "valid_responses": [],
        "patterns": {},
        "confirmation": True
    },
    "declaration": {
        "questions": 0,
        "fields": [
            "formDeclaration"
        ],
        "valid_responses": [],
        "patterns": {},
        "confirmation": True
    }
}

if __name__ == '__main__':
    print("Private Limited Company Registration Workflow Loaded Successfully!")
