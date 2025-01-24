import azure.functions as func
import logging
import os
import requests
import json

# from chat_app import complete_and_print
from expertApp.MPF_app import answerInSpecific

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="mpbot_trigger")
def mpbot_trigger(req: func.HttpRequest) -> func.HttpResponse:

    logging.info('Python HTTP trigger function processed a request.')
    
    message     = req.params.get('message')    
    phone       = req.params.get('phone')
    collection  = req.params.get('collection')    


#   response = complete_and_print("Generate the response in less than 100 words for :" + message)
    response = answerInSpecific(message, "sess001",  "MPdata")
    
    if not message:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            message = req_body.get('message')


    if message:
        return func.HttpResponse(f"{response}")
    else:
        return func.HttpResponse(
             "Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
