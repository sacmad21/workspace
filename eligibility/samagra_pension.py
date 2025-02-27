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
