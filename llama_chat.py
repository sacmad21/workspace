# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed according to the terms of the Llama 3 Community License Agreement.

import langchain
from langchain.llms import Replicate
import os
import requests
import json


class WhatsAppClient:

    API_URL = "https://graph.facebook.com/v18.0/" 
    WHATSAPP_API_TOKEN = "EAARfYvT6wOgBO2sQjzTldBuk5bZCivHYkqZBqneIizE65ZBohO8nMHv7HJSJPUImPvugSR2DA6gBEXZBnvzDhOsYdnENuHZA1I7aWX4vhcbSCfBbcV9PhbyGQdyszTEXxX8ZCSqQ44lPuz1JWuZBmQftnZAakUDwrwZAdEtU46ZAFsDwxYWEsIQE9zDxcoZCrHkohvzmd5nsa9ZCZAYgwyImQObf35vxO"
    WHATSAPP_CLOUD_NUMBER_ID = "441143062411889"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {self.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json",
        }
        self.API_URL = self.API_URL + self.WHATSAPP_CLOUD_NUMBER_ID 


    def send_text_message(self,message, phone_number):

        print("recipient phone number ::", phone_number, "::")

        payload = {
            "messaging_product": 'whatsapp',
            "to": phone_number,
            "text":
                {
                "body": message
                }          
            }


        print("Sending data to " + phone_number)

        response = requests.post(f"{self.API_URL}/messages", json=payload,headers=self.headers)

        print(response.status_code)

        assert response.status_code == 200, "Error sending message"
        return response.status_code



