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
