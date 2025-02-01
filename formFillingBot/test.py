import re

def testValidation() :
    check = { "pattern":"^\d{2}-\d{2}-\d{4}$","value":"27-10-200000"}

    result =  bool(re.match(check["pattern"], check["value"]))
    print (result)


testValidation()