import azure.functions as func
import json
from eligibility.util import send_whatsapp_message
from eligibility.msg_util import get_wa_data 
from datetime import datetime

#from eligibility.mukhyamantri_ladli_behna import check_ladli_behna_eligibility
#from eligibility.mukhyamantri_kisan_kalyan import check_kisan_kalyan_eligibility
#from eligibility.pm_kisan import check_pm_kisan_eligibility
#from eligibility.old_age_pension import check_old_age_pension_eligibility
#from eligibility.samagra_pension import check_samagra_pension_eligibility

import os 
import traceback


from dotenv import load_dotenv


user_data = {}
load_dotenv()



def check_ladli_behna_eligibility(user_data):

    if user_data["gender"] == "female" and \
        user_data["age"] >= 18 and \
        user_data["familyIncomeAnnual"] > 250000 and \
        user_data["residencyState"].lower() == "madhya pradesh" and \
        not user_data["incomeTaxPayerInFamily"] and \
        user_data["govtEmployeeInFamily"] not in ["yes"] and \
        user_data["pensionAmount"] < 10000:
        return "Eligible"
    return "Not Eligible"

def check_kisan_kalyan_eligibility(user_data):
    if user_data["landOwnershipType"] != "institutional" and \
        not user_data["constitutionalPostHolder"] and \
        not user_data["politicalPosition"] and \
        user_data["govtEmployeeInFamily"] not in ["yes"] and \
        user_data["pensionAmount"] < 10000 and \
        not user_data["incomeTaxPayerInFamily"] and \
        not user_data["professionalRegistration"]:
        return "Eligible"
    return "Not Eligible"


def check_pm_kisan_eligibility(user_data):
    if user_data["landOwnershipType"] == "institutional" or \
        user_data["constitutionalPostHolder"] or \
        user_data["politicalPosition"] or \
        user_data["govtEmployeeInFamily"] not in ["mts", "class iv", "group d", "no"] or \
        user_data["pensionAmount"] >= 10000 or \
        user_data["incomeTaxPayerInFamily"] or \
        user_data["professionalRegistration"]:
        return "Not Eligible"
    return "Eligible"


def check_old_age_pension_eligibility(user_data):
    if user_data["age"] >= 60 and \
        (user_data["bplStatus"] or \
            user_data["familyIncomeAnnual"] < 10000):
        return "Eligible"
    return "Not Eligible"

def check_samagra_pension_eligibility(user_data):
    if user_data["destituteStatus"] and \
        user_data["age"] >= 60:
        return "Eligible"
    if user_data["maritalStatus"] == "widow" and \
        user_data["age"] >= 18 and not user_data["incomeTaxPayerInFamily"]:
        return "Eligible"
    if user_data["maritalStatus"] == "unmarried" and \
        user_data["age"] >= 50 and not user_data["incomeTaxPayerInFamily"]:
        return "Eligible"
    if user_data["maritalStatus"] == "abandoned" and \
        18 <= user_data["age"] <= 59 and user_data["bplStatus"]:
        return "Eligible"
    if user_data["disabilityPercentage"] >= 40 and \
        user_data["age"] >= 6 and \
            not user_data["incomeTaxPayerInFamily"]:
        return "Eligible"
    if user_data["residentOfOldAgeHome"] and \
        user_data["age"] >= 60:
        return "Eligible"
    return "Not Eligible"



def validate(variable: str, value: str):
    """
    Validates input data based on the variable type.
    
    :param variable: Name of the variable to validate
    :param value: User input value as a string
    :return: (bool, str) Tuple where bool indicates success, and str provides an error message or converted value
    """

    # Integer validation for numerical fields
    if variable in ["age", "incomePerMonth", "familyIncomeAnnual", "pensionAmount", "disabilityPercentage"]:
        try:
            value = int(value)
            if value < 0:
                return False, f"{variable} cannot be negative."
            return True, value
        except ValueError:
            return False, f"Invalid input for {variable}. Please enter a valid number."

    # Gender validation
    if variable == "gender":
        valid_genders = ["male", "female"]
        if value.lower() in valid_genders:
            return True, value.lower()
        return False, "Invalid gender. Please enter 'male' or 'female'."

    # Residency state validation
    if variable == "residencyState":
        if value.strip():
            return True, value.title()  # Capitalizing state name
        return False, "Residency state cannot be empty."

    # Marital status validation
    if variable == "maritalStatus":
        valid_statuses = ["married", "unmarried", "widow", "divorcee", "deserted", "abandoned"]
        if value.lower() in valid_statuses:
            return True, value.lower()
        return False, f"Invalid marital status. Choose from {valid_statuses}."

    # Land ownership type validation
    if variable == "landOwnershipType":
        valid_types = ["personal", "institutional", "none"]
        if value.lower() in valid_types:
            return True, value.lower()
        return False, f"Invalid land ownership type. Choose from {valid_types}."

    # Yes/No validation for boolean fields
    yes_no_fields = [
        "constitutionalPostHolder", "politicalPosition", "incomeTaxPayerInFamily",
        "professionalRegistration", "bplStatus", "residentOfOldAgeHome", "destituteStatus", "honoraryWorker"
    ]
    
    if variable in yes_no_fields:
        if value.lower() in ["yes", "no"]:
            return True, value.lower() == "yes"  # Convert to boolean
        return False, f"Invalid input for {variable}. Please enter 'yes' or 'no'."

    # Government employee status validation
    if variable == "govtEmployeeInFamily":
        valid_options = ["yes", "no", "mts", "class iv", "group d"]
        if value.lower() in valid_options:
            return True, value.lower()
        return False, f"Invalid government employee status. Choose from {valid_options}."

    return False, f"Unknown variable '{variable}'. Please check input."



def getReadiness(user_data, phone_number, msg) :
    
    session = user_data[phone_number]

    if  session["status"] == "completed" :
        wa_message = f"Dear citizen, eligibility check for you is already completed."
        send_whatsapp_message(phone_number, wa_message)
        return False, func.HttpResponse(body=json.dumps({"status": "success", "message": wa_message}), mimetype="application/json")


    if  session["status"] == "started" :
        
        session["status"] = "ready"
        wa_message = "Welcome to Eligibiltiy Test for MP goverment schems: Should we proceed ? yes / no "
        send_whatsapp_message(phone_number, wa_message)
        return False, func.HttpResponse(body=json.dumps({"status": "success", "message": wa_message}), mimetype="application/json")


    if  session["status"] == "ready" and msg.lower() == "no":
        wa_message = f"Dear citizen, please get back to us for eligibility check, whenever required"
        send_whatsapp_message(phone_number, wa_message)
        session["status"] = "started"
        
        return False, func.HttpResponse(body=json.dumps({"status": "success", "message": wa_message}), mimetype="application/json")


    if session["status"] == "ready" and msg.lower() == "yes" :
        wa_message = f"we are ready for eligibility check, Answer following questions one by one."        
        send_whatsapp_message(phone_number, wa_message)
        session["status"] = "in-progress"

    return True, func.HttpResponse(body=json.dumps({"status": "success", "message": "No Action"}), mimetype="application/json")       




def post_webhook(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger for WhatsApp Webhook.
    """
    try:
        print("\nReuest :::", req)
        req_body = req.get_json()
        data = req.get_json()

        print("\nReuest :::", req_body)
        
#        message_data = req_body["entry"][0]["changes"][0]["value"]["messages"][0]        
#        phone_number = message_data["from"]
#        message_text = message_data["text"]["body"].strip().lower()

        M = get_wa_data(data)

        phone_number = M["phone"]
        message_text = M["text"]        
        
        print(f"\n\n-----------------------------WA incoming -------------------------\n")
        print(M)




        print("Stage-1 : Messaged Received ", phone_number, message_text)

        if phone_number not in user_data:
            user_data[phone_number] = { "status":"started" }

        isReady, httpmsg = getReadiness(user_data, phone_number, message_text)

        if isReady == False :
            return httpmsg


        user_session = user_data[phone_number]
        wa_message = "try to provide some intputs"

        if  "step" in user_session : 
            variable = user_session["step"]
            valid, error_message = validate(variable, message_text)

            if valid :
                user_session[variable] =  message_text
            else :
                wa_message = f"{message_text} is invalid for {variable}"
                wa_message = error_message
                send_whatsapp_message(phone_number, wa_message)
                return func.HttpResponse(body=json.dumps({"status": "success", "message": wa_message}), mimetype="application/json")


        # Step-by-step input collectio
#         "age": int(input("Enter your age: ")),

        if "age" not in user_session:
            wa_message = "Enter your age:"
            send_whatsapp_message(phone_number, wa_message)
            user_session["step"] = "age"


#       "gender": input("Enter your gender (male/female): ").lower(),
        elif "gender" not in user_session:
            wa_message = "Enter your gender (male/female):"

            user_session["age"] = int(message_text)
            send_whatsapp_message(phone_number, wa_message)
            user_session["step"] = "gender"

#       "incomePerMonth": int(input("Enter your monthly income (₹): ")),
        elif "incomePerMonth" not in user_session:
            wa_message = "Enter your monthly income (₹):"

            user_session["gender"] = message_text
            send_whatsapp_message(phone_number, wa_message)
            user_session["step"] = "incomePerMonth"

#        "familyIncomeAnnual": int(input("Enter your family's annual income (₹): ")),
        elif "familyIncomeAnnual" not in user_session:
            wa_message = "Enter your family's annual income (₹):"

            user_session["incomePerMonth"] = int(message_text)
            send_whatsapp_message(phone_number, wa_message)
            user_session["step"] = "familyIncomeAnnual"


#       "residencyState": input("Enter your state of residence: "),
        elif "residencyState" not in user_session:
            wa_message = "Enter your state of residence:"

            user_session["familyIncomeAnnual"] = int(message_text)
            send_whatsapp_message(phone_number, wa_message )
            user_session["step"] = "residencyState"

#           "maritalStatus": input("Enter your marital status (married/unmarried/widow/divorcee/deserted/abandoned): ").lower(),
        elif "maritalStatus" not in user_session:
            wa_message = "Enter your marital status (married/unmarried/widow/divorcee/deserted/abandoned):"

            user_session["residencyState"] = message_text
            send_whatsapp_message(phone_number, wa_message)
            user_session["step"] = "maritalStatus"

#           "honoraryWorker": input("Are you an honorary worker (Anganwadi/ASHA worker)? (yes/no): ").lower() == "yes"
        elif "honoraryWorker" not in user_session:
            wa_message = "Are you an honorary worker (Anganwadi/ASHA worker)? (yes/no):"
            user_session["maritalStatus"] = message_text
            send_whatsapp_message(phone_number, wa_message)
            user_session["step"] = "honoraryWorker"

#           "landOwnershipType": input("Do you own land? (personal/institutional/none): ").lower(),
        elif "landOwnershipType" not in user_session:
            wa_message = "Do you own land? (personal/institutional/none):"

            user_session["honoraryWorker"] = message_text.lower() == "yes"
            send_whatsapp_message(phone_number, wa_message )
            user_session["step"] = "landOwnershipType"


#        "incomeTaxPayerInFamily": input("Has any family member paid income tax in the last year? (yes/no): ").lower() == "yes",
        elif "incomeTaxPayerInFamily" not in user_session:
            wa_message = "Has any family member paid income tax in the last year? (yes/no):"

            user_session["landOwnershipType"] = message_text.lower()
            send_whatsapp_message(phone_number, wa_message )
            user_session["step"] = "incomeTaxPayerInFamily"

#        "professionalRegistration": input("Are you a practicing Doctor, Engineer, Lawyer, CA, or Architect? (yes/no): ").lower() == "yes",
        elif "professionalRegistration" not in user_session:
            wa_message = "Are you a practicing Doctor, Engineer, Lawyer, CA, or Architect? (yes/no): "

            user_session["incomeTaxPayerInFamily"] = message_text.lower() == "yes"
            send_whatsapp_message(phone_number, wa_message )
            user_session["step"] = "professionalRegistration"




#        "constitutionalPostHolder": input("Has any family member held a constitutional post? (yes/no): ").lower() == "yes",
        elif "constitutionalPostHolder" not in user_session:
            wa_message = "Has any family member held a constitutional post? (yes/no): "

            user_session["professionalRegistration"] = message_text.lower() == "yes"
            send_whatsapp_message(phone_number, wa_message )
            user_session["step"] = "constitutionalPostHolder"

#        "politicalPosition": input("Has any family member been an MP, MLA, Minister, Mayor, or Panchayat President? (yes/no): ").lower() == "yes",
        elif "politicalPosition" not in user_session:
            wa_message = "Has any family member been an MP, MLA, Minister, Mayor, or Panchayat President? (yes/no): "

            user_session["constitutionalPostHolder"] = message_text.lower() == "yes"
            send_whatsapp_message(phone_number, wa_message )
            user_session["step"] = "politicalPosition"

#        "govtEmployeeInFamily": input("Is any family member a government employee? (yes/no/MTS/Class IV/Group D): ").lower(),
        elif "govtEmployeeInFamily" not in user_session:
            wa_message = "Is any family member a government employee? (yes/no/MTS/Class IV/Group D): "

            user_session["politicalPosition"] = message_text.lower() == "yes"
            send_whatsapp_message(phone_number, wa_message )
            user_session["step"] = "govtEmployeeInFamily"

#        "pensionAmount": int(input("Enter pension amount received by any family member (₹): ")),
        elif "pensionAmount" not in user_session:
            wa_message = "Enter pension amount received by any family member (₹): "

            user_session["govtEmployeeInFamily"] = message_text.lower()
            send_whatsapp_message(phone_number, wa_message )
            user_session["step"] = "pensionAmount"

#        "disabilityPercentage": int(input("Enter disability percentage (if none, enter 0): ")),
        elif "disabilityPercentage" not in user_session:
            wa_message = "Enter disability percentage (if none, enter 0):  "

            user_session["pensionAmount"] = int(message_text)
            send_whatsapp_message(phone_number, wa_message )
            user_session["step"] = "disabilityPercentage"


#        "residentOfOldAgeHome": input("Are you living in an old age home? (yes/no): ").lower() == "yes",
        elif "residentOfOldAgeHome" not in user_session:
            wa_message = "Are you living in an old age home? (yes/no): "

            user_session["disabilityPercentage"] = int(message_text)
            send_whatsapp_message(phone_number, wa_message )
            user_session["step"] = "residentOfOldAgeHome"


#        "destituteStatus": input("Are you a destitute elderly person? (yes/no): ").lower() == "yes",
        elif "destituteStatus" not in user_session:
            wa_message = "Are you a destitute elderly person? (yes/no): "

            user_session["residentOfOldAgeHome"] = message_text.lower() == "yes"
            send_whatsapp_message(phone_number, wa_message )
            user_session["step"] = "destituteStatus"



#           "bplStatus": input("Are you from a Below Poverty Line (BPL) family? (yes/no): ").lower() == "yes",
        elif "bplStatus" not in user_session:
            wa_message = "Are you from a Below Poverty Line (BPL) family? (yes/no): "

            user_session["destituteStatus"] = message_text.lower() == "yes"
            send_whatsapp_message(phone_number, wa_message )
            user_session["step"] = "bplStatus"

        else:
            user_session["bplStatus"] = message_text.lower() == "yes"


            print("Stage-2 : Data is all received ", user_session)


            # Run eligibility checks
            eligibility_results = {
                "Mukhyamantri Ladli Behna Yojna": check_ladli_behna_eligibility(user_session),
                "Mukhyamantri Kisan Kalyan Yojna": check_kisan_kalyan_eligibility(user_session),
                "Pradhan Mantri Kisan Samman Nidhi": check_pm_kisan_eligibility(user_session),
                "Indira Gandhi National Old Age Pension Scheme": check_old_age_pension_eligibility(user_session),
                "Samagra Samajik Suraksha Pension Yojna": check_samagra_pension_eligibility(user_session),
            }

            
            # Send eligibility results
            result_message = "\n### *Your* *Eligibility* *Results* ###\n"
            for scheme, status in eligibility_results.items():
                result_message += f"{scheme}: {status}\n"

            wa_message = result_message

            send_whatsapp_message(phone_number, wa_message)
            user_session["status"] = "completed"


            # Clear user session
            user_data.pop(phone_number, None)

        return func.HttpResponse(body=json.dumps({"status": "success", "message": wa_message}), mimetype="application/json")


    except Exception as e:
        print("\nError occured :::", e)
        traceback.print_exc() 
        return func.HttpResponse(f"Error: {str(e)}", status_code=400)
    


    # Function for handling GET requests (webhook verification)
def get_webhook(req: func.HttpRequest) -> func.HttpResponse:

    
    WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")
    mode = req.params.get("hub.mode")
    token = req.params.get("hub.verify_token")
    challenge = req.params.get("hub.challenge")

    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        print("Webhook verified successfully!")
        return func.HttpResponse(challenge, status_code=200)
    else:
        print("Webhook not verified ", token, " not equal to" ,WEBHOOK_VERIFY_TOKEN)
        return func.HttpResponse("Forbidden", status_code=403)

