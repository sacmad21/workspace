import logging
import pdfkit
from jinja2 import Environment, FileSystemLoader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from weasyprint import HTML
from xhtml2pdf import pisa
import os
from datetime import date
import json


template_path = "./formFillingBot/templates"


def generate_pdf_from_template(user_id, data, template_name):
    
    """Generate a PDF for the given form using a template engine."""
    
    try:
        # Load the Jinja2 template
        print("Start PDF form generation ::", template_name, "\nForm data:::\n" , data)    
        env = Environment(loader=FileSystemLoader(f"{template_path}/{template_name}"))
        template = env.get_template(f"out_template.html")

        # Render the template with form data
        html_content = template.render(form_data=data)

        HTML(string=html_content).write_pdf(f"./formFillingBot/forms/{user_id}_{template_name}1form.pdf")

        html_path = f'./formFillingBot/forms/{user_id}{template_name}1.html'
        html_file = open(html_path, 'w')
        html_file.write(html_content)
        html_file.close()


        print(f"Now converting {user_id}.html ... ")
        pdf_path = f"./formFillingBot/forms/{user_id}_{template_name}2form.pdf"    
        html2pdf(html_path, pdf_path)   



        # Define PDF output file
        pdf_filename = f"./formFillingBot/forms/{user_id}_{template_name}3form.pdf"
        pdf_path = f"{pdf_filename}"

        logging.info(f"PDF generated successfully: {pdf_path}")
        return pdf_path
    except Exception as e:
        logging.error(f"Failed to generate PDF: {e}")
        return None


def html2pdf(html_path, pdf_path):
    """
    Convert html to pdf using pdfkit which is a wrapper of wkhtmltopdf
    """
    options = {
        'page-size': 'Letter',
        'margin-top': '0.35in',
        'margin-right': '0.35in',
        'margin-bottom': '0.35in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None
    }
    with open(html_path) as f:
        pdfkit.from_file(f, pdf_path, options=options)

def get_date():
    "Get today's date in German format"
    today = date.today()
    return today.strftime("%d.%m.%Y")


def testFormGeneration() :
    print(" -------------- ")

    scheme = "grih_adhar_goa"

    data_file = f"{template_path}/{scheme}/sample_form_data.json"

    with open(data_file) as json_file:
        form_data = json.load(json_file) 
        generate_pdf_from_template("917666819468",form_data,    scheme)


testFormGeneration()
