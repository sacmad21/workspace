
def get_wa_message_data(data) :

    sender = "NA"
    message_text = "NA"
    
    if "entry" in data:
        for entry in data["entry"]:
            for change in entry["changes"]:
                if "messages" in change["value"]:

                    for message in change["value"]["messages"]:

                        print("Incomding message :" , message)

                        sender = message["from"]
                        message_text = message.get("text", {}).get("body", "").strip().lower()

                        print("Sender::", sender)
                        print("Message::", message_text)

                        return sender, message_text

    return sender, message_text






def get_wa_data(message):
    try:
        entry = message.get("entry", [])[0]  # Get the first entry
        changes = entry.get("changes", [])[0]  # Get the first change
        value = changes.get("value", {})

        phone = None
        timestamp = None
        messageid = None
        convid = None
        text = None
        sender_name = None


        # Extract phone number from contacts (if available)
        contacts = value.get("contacts", [{}])[0]

#       phone = contacts.get("wa_id")

        sender_name = contacts.get("profile", {}).get("name", "")

        # Check for message statuses (read/delivered, etc.)
        if "statuses" in value:
            statuses = value.get("statuses", [{}])[0]
            phone = statuses.get("recipient_id", phone)  # Prefer recipient_id
            timestamp = statuses.get("timestamp")
            messageid = statuses.get("id")
            convid = statuses.get("conversation", {}).get("id")

        # Check for actual messages (incoming messages)
        elif "messages" in value:
            messages = value.get("messages", [{}])[0]
            phone = messages.get("from", phone)  # Prefer sender
            timestamp = messages.get("timestamp")
            messageid = messages.get("id")

            # Extract conversation ID if context is present
            context = messages.get("context", {})
            convid = context.get("id", convid)

            # Extract text from different message types
            if messages.get("type") == "text":
                text = messages.get("text", {}).get("body", "")
            elif messages.get("type") == "interactive":
                interactive = messages.get("interactive", {})
                if interactive.get("type") == "button_reply":
                    text = interactive.get("button_reply", {}).get("id", "")
                elif interactive.get("type") == "list_reply":
                    text = interactive.get("list_reply", {}).get("id", "")

        return {
            "phone": phone,
            "sender_name": sender_name,
            "timestamp": timestamp,
            "messageid": messageid,
            "convid": convid,
            "text": text
        }
    
    except Exception as e:
        print(f"Error extracting WhatsApp data: {e}")
        return None




# Example usage
incoming_data1 = {
    'object': 'whatsapp_business_account',
    'entry': [
        {
            'id': '1317068292871401',
            'changes': [
                {'value': 
                    {
                        'messaging_product': 'whatsapp', 'metadata': 
                        {
                            'display_phone_number': '15551461560', 'phone_number_id': '596950216828508'
                        }, 
                        'contacts': [
                            {'profile': {'name': 'Sachin Khaire'}, 'wa_id': '917666819468'}
                        ], 
                        'messages': [
                            {
                                'context': {'from': '15551461560', 'id': 'wamid.HBgMOTE3NjY2ODE5NDY4FQIAERgSQUUzQkY2MEVBODE4NEJFQUVDAA=='}, 
                                'from': '917666819468', 
                                'id': 'wamid.HBgMOTE3NjY2ODE5NDY4FQIAEhggQUZBNDgwMTA3MUJCMzMxOTA5MDlBRjFFRUQxOURERDEA', 
                                'timestamp': '1740651854', 
                                'type': 'interactive', 
                                'interactive': 
                                    {
                                    'type': 'button_reply', 
                                    'button_reply': 
                                        {
                                        'id': 'cancel', 'title': 'Cancel Appointment'
                                        }
                                    }
                            }
                        ]
                    }, 'field': 'messages'
                }
            ]
        }
    ]
}



interactivemsg1 = {'object': 'whatsapp_business_account', 'entry': [
        {'id': '1317068292871401', 'changes': [
                {'value': {'messaging_product': 'whatsapp', 'metadata': {'display_phone_number': '15551461560', 'phone_number_id': '596950216828508'
                        }, 'contacts': [
                            {'profile': {'name': 'Sachin Khaire'
                                }, 'wa_id': '917666819468'
                            }
                        ], 'messages': [
                            {'context': {'from': '15551461560', 'id': 'wamid.HBgMOTE3NjY2ODE5NDY4FQIAERgSRjJBOTM4NTlBNjFCRjdFRDg1AA=='
                                }, 'from': '917666819468', 'id': 'wamid.HBgMOTE3NjY2ODE5NDY4FQIAEhgWM0VCMDZFNEZDRDBGQzIzNTkwOEQyOQA=', 'timestamp': '1740678401', 'type': 'interactive', 'interactive': {'type': 'button_reply', 'button_reply': {'id': 'schedule', 'title': 'Schedule Appointment'
                                    }
                                }
                            }
                        ]
                    }, 'field': 'messages'
                }
            ]
        }
    ]
}

