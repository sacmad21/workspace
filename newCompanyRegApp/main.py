import logging
import azure.functions as func
import json
from openai import OpenAI
import traceback

from newCompanyRegApp.validation import validate_field, validate_step, validate_final_form

from newCompanyRegApp.util import (
    get_user_session,
    save_user_data,
    save_document,
    move_to_next_step,
    validate_and_update_session,
    send_message_via_whatsapp,
    prompts,
    openai_api_key,
    WEBHOOK_VERIFY_TOKEN,
    validation_rules,
    fields
    
)

def extract_fields_with_openai(prompt, user_input, session, step_fields):
    """Use OpenAI to extract fields, generate the next prompt, handle language confirmation, and determine step completion."""
    
    print("In OpenAI call ::\nPrompt:\n", prompt, "\nUSER:: ",user_input, "\nSESSION:: ",session )

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


        print("In OpenAI call ::\nSystem Prompt :::\n", openai_prompt )


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
        response_content = text.content.strip()
        print("\n\n\n\nGPT Response :::::::::::::::::: \n" , response_content)

        # Parse OpenAI's response
        parsed_response = json.loads(response_content)
        extracted_fields = parsed_response.get("fields", {})
        next_prompt = parsed_response.get("nextPrompt", "")
        step_complete = parsed_response.get("stepComplete", False)
        user_final_confirmation = parsed_response.get("userFinalConfirmation", False)

        # Handle language detection or change
        detected_language = parsed_response.get("language", None)
        if detected_language and detected_language != current_language:
            session["language"] = detected_language
            next_prompt = f"Language changed to {detected_language}. All future questions will be in this language."

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
            if not messages:
                return func.HttpResponse(body=json.dumps({"status": "no_messages"}), mimetype="application/json")

            # Get message details
            message = messages[0]
            user_id = message["from"]
            session = get_user_session(user_id)
            current_step = session.get("current_step", "eligibility_check")
            language = session.get("language", "default")


            # Load prompt for the current step
            step_prompt = prompts.get(current_step, "")
            step_fields = fields.get(current_step, "")


            # Handle document uploads
            if message.get("type") == "document":
                document_url = message["document"]["link"]
                document_name = message["document"]["filename"]
                save_document(user_id, document_name, document_url)
                wa_message = f"Received your document: {document_name}."
                send_message_via_whatsapp(user_id, wa_message)
                return func.HttpResponse(body=json.dumps({"status": "success" , "message":wa_message }), mimetype="application/json")


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
                step_valid = validate_step(session.get("data", {}), current_step)
                if not step_valid:
                    wa_message = "The information provided for this step is incomplete or invalid. Please review and correct it."
                    send_message_via_whatsapp(user_id, wa_message)
                    return func.HttpResponse(body=json.dumps({"status": "success", "message":wa_message}), mimetype="application/json")
                
                elif user_final_confirmation :
                    move_to_next_step(session) 
                    wa_message = f"Thank your for your confirmation, we will proceed to Next Step."
                    send_message_via_whatsapp(user_id, wa_message)
                    return func.HttpResponse(body=json.dumps({"status": "success", "message":wa_message  }), mimetype="application/json")
                
                else :                  
                    session["confirmation_pending"] = True
                    collected_data = json.dumps(session["data"], indent=2)
                    wa_message = f"Here are the details you provided for this step:\n{collected_data}\n\nplease give your final confirmation ? (Reply 'Yes' to confirm or 'No' to edit)"
                    send_message_via_whatsapp(user_id, wa_message)
                    return func.HttpResponse(body=json.dumps({"status": "success", "message":wa_message  }), mimetype="application/json")

        # Handle completion
            if session.get("current_step") == "completed":
                if validate_final_form(session.get("data", {})):
                    wa_message = "All details and documents have been collected and validated. Thank you!"
                    send_message_via_whatsapp(user_id, wa_message)
                    return func.HttpResponse(body=json.dumps({"status": "success" , "message":wa_message }), mimetype="application/json")
                else:
                    wa_message =  "The final validation of your form failed. Please review your inputs."
                    send_message_via_whatsapp(user_id, wa_message)
                    return func.HttpResponse(body=json.dumps({"status": "success", "message":wa_message}), mimetype="application/json")



            # Send next step prompt
            wa_message = next_prompt or prompts.get(session["current_step"], "Thank you! Workflow is completed.")
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
