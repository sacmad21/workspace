# Import required modules

import logging
import os
import requests
from azure.functions import HttpRequest, HttpResponse
import azure.functions as func

#from formFillingBot.main import get_webhook, post_webhook 
# from eligibility.main import get_webhook, post_webhook
# from expertApp.expertBot import *
from clinicBot.main import *


app = func.FunctionApp( http_auth_level=func.AuthLevel.ANONYMOUS )
@app.route(route="webhook")
def webhook(req: HttpRequest) -> HttpResponse:
    if req.method == "POST":
        print("\n\n\n\nWhatsApp Request", req.get_json() )
        return post_webhook(req)
    elif req.method == "GET":
        return get_webhook(req)
    else:
        return HttpResponse("Method Not Allowed", status_code=405)
    