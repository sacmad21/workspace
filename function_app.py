# Import required modules
import logging
import os
import requests
from azure.functions import HttpRequest, HttpResponse
import azure.functions as func
from newCompanyRegApp.main import get_webhook, post_webhook 


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
@app.route(route="webhook")
def webhook(req: HttpRequest) -> HttpResponse:
    if req.method == "POST":
        return post_webhook(req)
    elif req.method == "GET":
        
        return get_webhook(req)
    else:
        return HttpResponse("Method Not Allowed", status_code=405)
    