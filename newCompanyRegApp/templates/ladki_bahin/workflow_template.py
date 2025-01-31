
workflow = {
        "welcome": {
            "welcome": "Welcome, Are you interested to apply for Ladki Bahin Yojana of Maharashtra Goverment ? (Yes/No)",
            "questions": 1,
            "fields" : ["isInterested"],
            "valid_responses": ["Yes", "No"],
            "confirmation":True
        },

        "eligibility_check": {
            "eligibility_check": "Let’s check your eligibility:\n1. Are you a resident of Maharashtra? (Yes/No)\n2. Are you a girl child aged between 18 and 35 years? (Yes/No)\n3. Do you belong to a Below Poverty Line (BPL) family? (Yes/No)\n4. Have you completed education up to Class 10? (Yes/No)\n5. Are you unmarried or divorced? (Yes/No):",

            "questions": 5,
            "fields" : ["isResident_of_Maharashtra", "isGirlChildBetween18and35Years", "isBPL","isEducationUptoClass10", "isUnmarriedOrDivorced"],
            "valid_responses": ["Yes", "No"],
            "confirmation":True
        },

        "basic_details": {
            "basic_details": "Please provide your personal details:\n1. What is your Full Name ?\n2. What is your Father's or Guardian's Name ?\n3. Date of Birth (DD-MM-YYYY) ?\n4. What is your Aadhaar Number ?\n5. What is your Mobile Number ?\n6. What is your Address (House Number/Street, Village/Town, District, PIN Code):",

            "fields": ["fullName","fatherOrGuardianName","DOB","aadharNumber","mobileNumber","address"],
            "patterns": {
                "DOB": r"^\d{2}-\d{2}-\d{4}$",  # DD/MM/YYYY
                "aadharNumber": r"^\d{12}$",
                "mobileNumber": r"^\d{10}$"
            },
            "confirmation":True

        },

        "bank_details": {
            
            "bank_details": "Please provide your bank account details:\n1. What is account holder's name ?\n2. What is name of bank ?\n3. What is branch name ? \n4. What is account number:\n5. What is IFSC code ?",

            "fields": ["bankName","branchName","accountHolderName","accountNumber","ifscCode"],
            "patterns": {
                "ifscCode": r"^[A-Z]{4}0[A-Z0-9]{6}$"
            },
            "confirmation":True

        },
        "educational_details": {
            "educational_details": "Provide your educational qualifications:\n1. What is name of the School/Institution ? (last attended):\n2. What is the year of passing Class 10:\n3. How many Marks are obtained in Class 10 class?\n4. Do you have a valid passing certificate? (Yes/No):",

            "fields": ["nameOfInstution","yearOfPassingClass10","marksObtained","isValid1Certificate"],
            "patterns": {
                "yearOfPassingClass10": r"^\d{4}$",
                "marksOntainedIn10Class": r"^\d{1,3}$"
            },
            "confirmation":True

        },
        "family_income": {
            "family_income": "Please provide your family's income details:\n1. What is Total Annual Family Income (in INR):\n2. What are Source(s) of Income ? (e.g., Agriculture, Daily Wage, etc.):\n3. Do you have a valid BPL card? (Yes/No):",

            "fields": ["annualFamilyIncome","sourceOfIncome","idBplCardAvailable"],
            "patterns": {
                "annualFamilyIncome": r"^\d+(\.\d{1,2})?$"  # Valid number format
            },
            "confirmation":True

        },

        "document_upload": {
            "document_upload": f"Upload the following mandatory documents:\n{', '.join(mandatory_documents)}.\nPlease upload one document at a time.",
            "fields": ["isAdharCardUploaded","isClass10CertificateUploaded","isBPLCardUploaded","isCancelledChequeUploaded", "isResidentialProofUploaded"],
            "confirmation":True
        },

        "declaration": {
            "declaration": "Please confirm the following declaration:\n'I hereby declare that all the information provided is true to the best of my knowledge, and I understand that any false information may lead to the rejection of my application.'\nType 'YES' to agree and complete the process.",

            "fields": ["formDeclaration"],
            "confirmation":True
        }
    }

workflow_steps = ["welcome","eligibility_check", "basic_details", "bank_details", "educational_details", "family_income", "document_upload", "declaration"]

mandatory_documents = ["Aadhaar Card", "Class 10 Certificate", "BPL Card", "Bank Passbook/Cancelled Cheque", "Residential Proof"]        
