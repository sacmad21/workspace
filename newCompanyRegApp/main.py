import logging
import azure.functions as func
import json
from openai import OpenAI
import traceback

from newCompanyRegApp.validation import validate_field, validate_step, validate_final_form

from newCompanyRegApp.util import *

def extract_fields_with_openai(prompt, user_input, session, step_fields):
    """Use OpenAI to extract fields, generate the next prompt, handle language confirmation, and determine step completion."""
    
    print("Preparing to Call ::::::::::::::::::::\nPrompt:\n", prompt, "\nUSER:: ",user_input, "\nSESSION:: ",session,"\n\n=================================")

    response_content = ""
    try:
        # Include previous responses and language preference in the context
        existing_responses = session.get("data", {})
        current_language = session.get("language", "default")
        previous_prompt = session.get("wa_message","Welcome")

        context = (
            f"Previously provided answers:\n{json.dumps(existing_responses, indent=2)}\n"
            f"Current language: {current_language}\n"
        )

        # OpenAI prompt explicitly aligned with the workflow and current step
        openai_prompt = (
            f"You are a multilingual assistant designed to assist with form filling.\n"
            f"Your tasks are:\n"
            f"1. Extract required fields {step_fields} from the user's input based on the following prompt:\n START_PROMPT::"
            f"   {prompt} ::END_PROMPT\n"
            f"2. Use the user's previous responses to avoid redundant questions.\n"
            f"3. Generate the next question or confirmation prompt in the user's preferred language.\n"
            f"4. Indicate whether the current step is complete.\n\n"
            f"Format your response as JSON only:\n"
            f"{{\n"
            f"  \"response\": \"<general_response>\",\n"
            f"  \"fields\": {{<extracted_fields>}},\n"
            f"  \"nextPrompt\": \"<next_question_or_confirmation>\",\n"
            f"  \"stepComplete\": <true_or_false>,\n"
            f"  \"language\": \"<detected_or_requested_language>\"\n"
            f"  \"userFinalConfirmation\":\"<true_or_false>"
            f"}}\n\n")
        
        context_part = f"Context:\n{context}\n\n"
        user_part    =    f"User Input:\n{user_input}\n"
        
        
        messages_all_in_sys=[
                {"role": "system",  "content": openai_prompt},
                {"role": "user",        "content": context_part },
                {"role": "system" ,     "content": previous_prompt },
                {"role": "user"     , "content": user_input }
            ]

        messages_inremental=[
                {"role": "system", "content": openai_prompt},
            ]

        # Try to generate conversation sequence so that exact response can be generated.
        past_message = []        
        #messages_inremental.append(past_message)
        #messages_inremental.append({"role": "user", "content": user_input })


        print("\nFinal Prompt :::\n", messages_all_in_sys )


#       client = OpenAI(api_key=openai_api_key)
        client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key="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",
            )
        LLM = "llama-3.3-70b-versatile"

        response = client.chat.completions.create(
            model=LLM,
            messages=messages_all_in_sys,
            max_tokens=500
        )
        choices: any = response.choices[0]
        text = choices.message
        response_content = text.content.strip().replace("\n"," ")
        print("\n\n\n\nGPT Response :::::::::::::::::: \n" , response_content)

        # Parse OpenAI's response
        parsed_response = json.loads(response_content)
        extracted_fields = parsed_response.get("fields", {})
        next_prompt = parsed_response.get("nextPrompt", "")
        step_complete = parsed_response.get("stepComplete", False)
        user_final_confirmation = parsed_response.get("userFinalConfirmation", False)


        # Handle language detection or change
        #detected_language = parsed_response.get("language", None)
        #if detected_language and detected_language != current_language:
        #    session["language"] = detected_language
        #    next_prompt = f"Language changed to {detected_language}. All future questions will be in this language."


        return extracted_fields, step_complete, next_prompt, user_final_confirmation


    except Exception as e:
        traceback.print_exc() 
        print("\nInvalid JSON ::::::::::: ", response_content , "\n=======================================================")
        logging.error(f"Error extracting fields with OpenAI: {e}")
        return {}, False, "Error processing your input. Please try again."






def post_webhook(req: func.HttpRequest) -> func.HttpResponse:
        """Handle incoming WhatsApp messages."""
        logging.info('Python HTTP trigger function processed a request.')
        wa_message = ""
        try:
            data = req.get_json()

            # Parse data received from WhatsApp API
            messages = data.get("entry", [])[0].get("changes", [])[0].get("value", {}).get("messages", [])
            print("\n POST from WHATSAPP    ::::::::::::::::::::\n", messages)

            if not messages:
                return func.HttpResponse(body=json.dumps({"status": "no_messages"}), mimetype="application/json")

            # Get message details
            message = messages[0]
            user_id = message["from"]
            session = get_user_session(user_id)
            current_step = session.get("current_step", FIRST_STEP)
            language = session.get("language", "default")


            # Load prompt for the current step
            step_prompt = prompts.get(current_step, "")
            step_fields = fields.get(current_step, "")


            # Handle document uploads
            if message.get("type") == "document":
                if "Link" in message["document"] :
                    document_url = message["document"]["link"]
                    document_name = message["document"]["filename"]
                    save_document_from_url(user_id, document_name, document_url)
                    wa_message = f"Received your document: {document_name}."
                    send_message_via_whatsapp(user_id, wa_message)
                    return func.HttpResponse(body=json.dumps({"status": "success" , "message":wa_message }), mimetype="application/json")
                
                elif "id" in message["document"] :
                    document_id = message["document"]["id"]
                    document_name = message["document"]["filename"]

                    # Step 1: Fetch document metadata
                    metadata = fetch_document_metadata(document_id)
                    if not metadata:
                        wa_message = "Failed to fetch document metadata. Check your internet, kindly upload the document again after sometime"
                        send_message_via_whatsapp(user_id, wa_message)
                        return func.HttpResponse(body=json.dumps({"status": "error", "message": wa_message}), mimetype="application/json")

                    media_url = metadata.get("url")
                    print("Media URL :: ", media_url)
                    if not media_url:
                        wa_message = "Document URL is missing in metadata. Please try again."
                        send_message_via_whatsapp(user_id, wa_message)
                        return func.HttpResponse(body=json.dumps({"status": "error", "message": wa_message}), mimetype="application/json")


            # Step 2: Download the document and upload to Azure Data Lake
                    document_url = download_document_from_WA_pushto_ADL(media_url, user_id, document_name)
                    if not document_url:
                        wa_message = "Failed to process the document. Please try again."
                        send_message_via_whatsapp(user_id, wa_message)
                        return func.HttpResponse(body=json.dumps({"status": "error", "message": wa_message}), mimetype="application/json")

                    # Step 3: Save the document URL to the user's session or database
                    save_document_from_url(user_id, document_name, document_url)
                    wa_message = f"Successfully received and saved your document: {document_name}. You can access it here: {document_url}"
                    user_message = f"Successfully uplaoded and saved document: {document_name}"
                    send_message_via_whatsapp(user_id, wa_message)
#                   return func.HttpResponse(body=json.dumps({"status": "success", "message": wa_message}), mimetype="application/json")
                    message["text"]["body"] = user_message


            # Handle text messages
            user_input = message["text"]["body"]
            print("\n ================================================================= Open AI Call  ", user_input)
            extracted_fields, step_complete, next_prompt, user_final_confirmation = extract_fields_with_openai(step_prompt, user_input, session, step_fields)

            print ("After Generating Response :: " , extracted_fields, step_complete, next_prompt)
            

            if extracted_fields :
            # Validate individual fields
                for field, value in extracted_fields.items():
                    valid = validate_field(current_step, field, value)
                    if not valid:
                        wa_message = f"The field '{field}' has an invalid value. Please correct it."
                        send_message_via_whatsapp(user_id, wa_message)
                        return func.HttpResponse(body=json.dumps({"status": "success", "message":wa_message}), mimetype="application/json")
                    else :
                        session["data"][field]=value      
                
                # Save valid data
                save_user_data(user_id, extracted_fields)



        # Validate the step
            if step_complete:
                print("\nCurrent step is complete ::::", current_step)
                step_valid = validate_step(session.get("data", {}), current_step)
                if not step_valid:
                    wa_message = "The information provided for this step is incomplete or invalid. Please review and correct it."
                    print("\nStep complete-",wa_message)
                    send_message_via_whatsapp(user_id, wa_message)
                    return func.HttpResponse(body=json.dumps({"status": "success", "message":wa_message}), mimetype="application/json")
                
                elif user_final_confirmation or  (not doStepConfirmationRequired(session)):
                    
                    move_to_next_step(session)                    

                    # This if block should proceed when any stage is left for completion.
                    if not session.get("current_step") == "completed":
                        wa_message = f"Thank your for your confirmation, we will proceed to Next Step."
                        print("\nStep complete-",wa_message)
                        send_message_via_whatsapp(user_id, wa_message)
                        return func.HttpResponse(body=json.dumps({"status": "success", "message":wa_message  }), mimetype="application/json")
                
                else :                  
                    session["confirmation_pending"] = True
                    collected_data = json.dumps(session["data"], indent=2)
                    wa_message = f"Here are the details you provided for this step:\n{collected_data}\n\nplease give your final confirmation ? (Reply 'Yes' to confirm or 'No' to edit)"
                    print("\nStep complete-",wa_message)
                    send_message_via_whatsapp(user_id, wa_message)
                    return func.HttpResponse(body=json.dumps({"status": "success", "message":wa_message  }), mimetype="application/json")


        # Handle completion
            if session.get("current_step") == "completed":
                if validate_final_form(session.get("form", {})):
                    wa_message = f"""All details and documents have been collected and validated. Thank you! \n Final Form data is {session.get("form_data")}"""
                    print("\nForm complete-",wa_message)
                    send_message_via_whatsapp(user_id, wa_message)
                    
                    finalizeForm(user_id, session)
                    
                    return func.HttpResponse(body=json.dumps({"status": "success" , "message":wa_message }), mimetype="application/json")
                else:
                    wa_message =  "The final validation of your form failed. Please review your inputs."
                    print("\nStep complete-",wa_message)
                    send_message_via_whatsapp(user_id, wa_message)
                    return func.HttpResponse(body=json.dumps({"status": "success", "message":wa_message}), mimetype="application/json")



            # Send next step prompt
            wa_message = next_prompt or prompts.get(session["current_step"], "Thank you! Workflow is completed.")
            print(wa_message)
            session["wa_message"] =  wa_message       

            send_message_via_whatsapp(user_id, wa_message)

            return func.HttpResponse(body=json.dumps({"status": "success", "message": next_prompt}), mimetype="application/json")

        except Exception as e:
            traceback.print_exc() 
            logging.error(f"Error processing request: {e}")
            return func.HttpResponse(body=json.dumps({"status": "error", "message": str(e)}), mimetype="application/json", status_code=500)










    # Function for handling GET requests (webhook verification)
def get_webhook(req: func.HttpRequest) -> func.HttpResponse:

    mode = req.params.get("hub.mode")
    token = req.params.get("hub.verify_token")
    challenge = req.params.get("hub.challenge")

    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        logging.info("Webhook verified successfully!")
        return func.HttpResponse(challenge, status_code=200)
    else:
        return func.HttpResponse("Forbidden", status_code=403)
