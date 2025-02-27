def check_old_age_pension_eligibility(user_data):
    if user_data["age"] >= 60 and \
        (user_data["bplStatus"] or \
            user_data["familyIncomeAnnual"] < 10000):
        return "Eligible"
    return "Not Eligible"
