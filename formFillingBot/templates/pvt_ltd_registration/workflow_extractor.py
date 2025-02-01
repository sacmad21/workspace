import json


# Load form workflow JSON file
def load_form_workflow(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        return json.load(file)


# Extract workflow components
def extract_workflow_components(form_workflow):
    workflow_steps = list(form_workflow.keys())
    
    mandatory_documents = form_workflow.get("document_upload", {}).get("fields", [])
    
    prompts = {
        step: form_workflow[step].get(step, "")
        for step in workflow_steps if step in form_workflow
    }
    
    fields = {
        step: form_workflow[step].get("fields", [])
        for step in workflow_steps if step in form_workflow
    }
    
    validation_rules = {
        step: {
            "questions": form_workflow[step].get("questions", 0),
            "fields": form_workflow[step].get("fields", []),
            "valid_responses": form_workflow[step].get("valid_responses", []),
            "patterns": form_workflow[step].get("patterns", {}),
            "confirmation": form_workflow[step].get("confirmation", False)
        }
        for step in workflow_steps if step in form_workflow
    }
    
    return workflow_steps, mandatory_documents, prompts, fields, validation_rules

# Generate workflow.py file
def generate_workflow_py(workflow_steps, mandatory_documents, prompts, fields, validation_rules, output_file="workflow.py"):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("# workflow.py\n\n")
        
        file.write("# Workflow Steps\n")
        file.write(f"workflow_steps = {json.dumps(workflow_steps, indent=4)}\n\n")
        
        file.write("# Mandatory Documents\n")
        file.write(f"mandatory_documents = {json.dumps(mandatory_documents, indent=4)}\n\n")
        
        file.write("# Workflow Prompts\n")
        file.write(f"prompts = {json.dumps(prompts, indent=4)}\n\n")
        
        file.write("# Workflow Fields\n")
        file.write(f"fields = {json.dumps(fields, indent=4)}\n\n")
        
        file.write("# Validation Rules\n")
        file.write(f"validation_rules = {json.dumps(validation_rules, indent=4)}\n\n")
        
        file.write("if __name__ == '__main__':\n")
        file.write("    print(\"Private Limited Company Registration Workflow Loaded Successfully!\")\n")

# Main Execution
if __name__ == "__main__":
    form_workflow = load_form_workflow("form_workflow.json")
    workflow_steps, mandatory_documents, prompts, fields, validation_rules = extract_workflow_components(form_workflow)
    generate_workflow_py(workflow_steps, mandatory_documents, prompts, fields, validation_rules)
    print("workflow.py has been generated successfully!")
