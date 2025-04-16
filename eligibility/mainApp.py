
from eligibility.mukhyamantri_ladli_behna import check_ladli_behna_eligibility
from eligibility.mukhyamantri_kisan_kalyan import check_kisan_kalyan_eligibility
from eligibility.pm_kisan import check_pm_kisan_eligibility
from eligibility.old_age_pension import check_old_age_pension_eligibility
from eligibility.samagra_pension import check_samagra_pension_eligibility


def get_user_input():
    """
    Collects user input for eligibility variables.
    """
    print("\n### Enter your details ###\n")
    
    return {
        "age": int(input("Enter your age: ")),
        "gender": input("Enter your gender (male/female): ").lower(),
        "incomePerMonth": int(input("Enter your monthly income (₹): ")),
        "familyIncomeAnnual": int(input("Enter your family's annual income (₹): ")),
        "residencyState": input("Enter your state of residence: "),
        "maritalStatus": input("Enter your marital status (married/unmarried/widow/divorcee/deserted/abandoned): ").lower(),
        "landOwnershipType": input("Do you own land? (personal/institutional/none): ").lower(),
        "constitutionalPostHolder": input("Has any family member held a constitutional post? (yes/no): ").lower() == "yes",
        "politicalPosition": input("Has any family member been an MP, MLA, Minister, Mayor, or Panchayat President? (yes/no): ").lower() == "yes",
        "govtEmployeeInFamily": input("Is any family member a government employee? (yes/no/MTS/Class IV/Group D): ").lower(),
        "pensionAmount": int(input("Enter pension amount received by any family member (₹): ")),
        "incomeTaxPayerInFamily": input("Has any family member paid income tax in the last year? (yes/no): ").lower() == "yes",
        "professionalRegistration": input("Are you a practicing Doctor, Engineer, Lawyer, CA, or Architect? (yes/no): ").lower() == "yes",
        "bplStatus": input("Are you from a Below Poverty Line (BPL) family? (yes/no): ").lower() == "yes",
        "disabilityPercentage": int(input("Enter disability percentage (if none, enter 0): ")),
        "residentOfOldAgeHome": input("Are you living in an old age home? (yes/no): ").lower() == "yes",
        "destituteStatus": input("Are you a destitute elderly person? (yes/no): ").lower() == "yes",
        "honoraryWorker": input("Are you an honorary worker (Anganwadi/ASHA worker)? (yes/no): ").lower() == "yes"
    }

def main():
    user_data = get_user_input()

    results = {
        "Mukhyamantri Ladli Behna Yojna": check_ladli_behna_eligibility(user_data),
        "Mukhyamantri Kisan Kalyan Yojna": check_kisan_kalyan_eligibility(user_data),
        "Pradhan Mantri Kisan Samman Nidhi": check_pm_kisan_eligibility(user_data),
        "Indira Gandhi National Old Age Pension Scheme": check_old_age_pension_eligibility(user_data),
        "Samagra Samajik Suraksha Pension Yojna": check_samagra_pension_eligibility(user_data),
    }

    print("\n### Eligibility Results ###")
    for scheme, status in results.items():
        print(f"{scheme}: {status}")

if __name__ == "__main__":
    main()
