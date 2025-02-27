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
