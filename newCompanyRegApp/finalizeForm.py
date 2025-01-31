import logging
from jinja2 import Environment, FileSystemLoader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

def generate_pdf_from_template(user_id, form_data, template_name="ladki_bahin_yojana"):
    """Generate a PDF for the given form using a template engine."""
    try:
        # Load the Jinja2 template
        template_path = "templates"
        env = Environment(loader=FileSystemLoader(template_path))
        template = env.get_template(f"{template_name}.html")

        # Render the template with form data
        html_content = template.render(form_data=form_data)

        # Define PDF output file
        pdf_filename = f"{user_id}_form.pdf"
        pdf_path = f"/tmp/{pdf_filename}"

        # Create a PDF
        c = canvas.Canvas(pdf_path, pagesize=A4)
        c.setFont("Helvetica", 12)
        y_position = 800

        # Render the HTML content into the PDF
        for line in html_content.split("\n"):
            c.drawString(100, y_position, line)
            y_position -= 20

        c.save()

        logging.info(f"PDF generated successfully: {pdf_path}")
        return pdf_path
    except Exception as e:
        logging.error(f"Failed to generate PDF: {e}")
        return None
