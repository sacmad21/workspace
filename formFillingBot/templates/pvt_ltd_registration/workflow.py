# workflow.py

# Workflow Steps
workflow_steps = [
    "welcome",
    "eligibility_check",
    "director_details",
    "shareholder_details",
    "company_details",
    "registered_office_details",
    "capital_structure",
    "digital_signatures",
    "document_upload",
    "declaration"
]

# Mandatory Documents
mandatory_documents = [
    "isPANUploaded",
    "isAadhaarUploaded",
    "isPassportUploaded",
    "isAddressProofUploaded",
    "isOfficeProofUploaded",
    "isNOCUploaded"
]

# Workflow Prompts
prompts = {
    "welcome": "Welcome! Are you interested in registering a new Private Limited Company in India? (Yes/No)",
    "eligibility_check": "Let's check your eligibility:\n1. Do you have at least 2 Directors? (Yes/No)\n2. Do you have at least 2 Shareholders (can be the same as directors)? (Yes/No)\n3. Is at least one Director an Indian Resident? (Yes/No)\n4. Have you checked the availability of a unique company name? (Yes/No)\n5. Do you have a registered office address in India? (Yes/No)",
    "director_details": "Please provide details of each director (Minimum 2 required):\n1. Full Name:\n2. Father's Name:\n3. Date of Birth (DD-MM-YYYY):\n4. PAN Number:\n5. Aadhaar Number:\n6. Mobile Number:\n7. Email ID:\n8. Residential Address:\n9. DIN (if available, else type 'Not Available'):",
    "shareholder_details": "Please provide details of each shareholder (Minimum 2 required):\n1. Full Name:\n2. Number of Shares to be Held:\n3. PAN Number:\n4. Aadhaar Number:\n5. Residential Address:",
    "company_details": "Provide details about your company:\n1. Proposed Company Name (3 options):\n2. Main Business Activities:",
    "registered_office_details": "Please provide details of your registered office:\n1. Address:\n2. Do you have an Electricity Bill / Rent Agreement? (Yes/No)\n3. Do you have a NOC from the owner (if rented)? (Yes/No)",
    "capital_structure": "Please provide the financial details of your company:\n1. Authorized Capital (Minimum \u20b91 lakh):\n2. Paid-up Capital:\n3. Percentage of Shareholding for Each Shareholder:",
    "digital_signatures": "Do all directors have Digital Signature Certificates (DSC)? (Yes/No)\nDo you need assistance in obtaining DSC? (Yes/No)",
    "document_upload": "Upload the following mandatory documents:\n1. PAN Card for each Director & Shareholder\n2. Aadhaar Card for each Director & Shareholder\n3. Passport (if applicable)\n4. Address Proof (Bank Statement / Utility Bill)\n5. Electricity Bill / Rent Agreement for Registered Office\n6. NOC from Office Owner (if rented)\nPlease upload one document at a time.",
    "declaration": "Please confirm the following declaration:\n'I hereby declare that all the information provided is true to the best of my knowledge, and I understand that any false information may lead to the rejection of my application.'\nType 'YES' to agree and complete the process."
}

# Workflow Fields
fields = {
    "welcome": [
        "isInterested"
    ],
    "eligibility_check": [
        "hasTwoDirectors",
        "hasTwoShareholders",
        "hasIndianResidentDirector",
        "hasUniqueCompanyName",
        "hasRegisteredOffice"
    ],
    "director_details": [
        "fullName",
        "fathersName",
        "DOB",
        "PAN",
        "Aadhaar",
        "mobileNumber",
        "emailID",
        "residentialAddress",
        "DIN"
    ],
    "shareholder_details": [
        "shareholderName",
        "sharesHeld",
        "shareholderPAN",
        "shareholderAadhaar",
        "shareholderAddress"
    ],
    "company_details": [
        "proposedCompanyName1",
        "proposedCompanyName2",
        "proposedCompanyName3",
        "businessActivities"
    ],
    "registered_office_details": [
        "officeAddress",
        "hasElectricityBillOrRentAgreement",
        "hasNOC"
    ],
    "capital_structure": [
        "authorizedCapital",
        "paidUpCapital",
        "shareholdingPercentage"
    ],
    "digital_signatures": [
        "hasDSC",
        "needsDSCAssistance"
    ],
    "document_upload": [
        "isPANUploaded",
        "isAadhaarUploaded",
        "isPassportUploaded",
        "isAddressProofUploaded",
        "isOfficeProofUploaded",
        "isNOCUploaded"
    ],
    "declaration": [
        "formDeclaration"
    ]
}

# Validation Rules
validation_rules = {
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
        "confirmation": True
    },
    "eligibility_check": {
        "questions": 5,
        "fields": [
            "hasTwoDirectors",
            "hasTwoShareholders",
            "hasIndianResidentDirector",
            "hasUniqueCompanyName",
            "hasRegisteredOffice"
        ],
        "valid_responses": [
            "Yes",
            "No"
        ],
        "patterns": {},
        "confirmation": True
    },
    "director_details": {
        "questions": 0,
        "fields": [
            "fullName",
            "fathersName",
            "DOB",
            "PAN",
            "Aadhaar",
            "mobileNumber",
            "emailID",
            "residentialAddress",
            "DIN"
        ],
        "valid_responses": [],
        "patterns": {
            "DOB": "^\\d{2}-\\d{2}-\\d{4}$",
            "PAN": "^[A-Z]{5}[0-9]{4}[A-Z]$",
            "Aadhaar": "^\\d{12}$",
            "mobileNumber": "^\\d{10}$"
        },
        "confirmation": True
    },
    "shareholder_details": {
        "questions": 0,
        "fields": [
            "shareholderName",
            "sharesHeld",
            "shareholderPAN",
            "shareholderAadhaar",
            "shareholderAddress"
        ],
        "valid_responses": [],
        "patterns": {
            "shareholderPAN": "^[A-Z]{5}[0-9]{4}[A-Z]$",
            "shareholderAadhaar": "^\\d{12}$"
        },
        "confirmation": True
    },
    "company_details": {
        "questions": 0,
        "fields": [
            "proposedCompanyName1",
            "proposedCompanyName2",
            "proposedCompanyName3",
            "businessActivities"
        ],
        "valid_responses": [],
        "patterns": {},
        "confirmation": True
    },
    "registered_office_details": {
        "questions": 0,
        "fields": [
            "officeAddress",
            "hasElectricityBillOrRentAgreement",
            "hasNOC"
        ],
        "valid_responses": [],
        "patterns": {},
        "confirmation": True
    },
    "capital_structure": {
        "questions": 0,
        "fields": [
            "authorizedCapital",
            "paidUpCapital",
            "shareholdingPercentage"
        ],
        "valid_responses": [],
        "patterns": {
            "authorizedCapital": "^\\d+(\\.\\d{1,2})?$",
            "paidUpCapital": "^\\d+(\\.\\d{1,2})?$"
        },
        "confirmation": True
    },
    "digital_signatures": {
        "questions": 0,
        "fields": [
            "hasDSC",
            "needsDSCAssistance"
        ],
        "valid_responses": [],
        "patterns": {},
        "confirmation": True
    },
    "document_upload": {
        "questions": 0,
        "fields": [
            "isPANUploaded",
            "isAadhaarUploaded",
            "isPassportUploaded",
            "isAddressProofUploaded",
            "isOfficeProofUploaded",
            "isNOCUploaded"
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
