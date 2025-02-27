import os
import logging
import requests
import traceback
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import base64
import io

# Together AI Configuration
TOGETHER_VISION_MODEL = "llava-v1.6-vicuna-13b"
TOGETHER_VISION_API_URL = "https://api.together.xyz/inference"
TOGETHER_VISION_API_KEY = os.getenv("GENAI_API_KEY")


def download_pdf(pdf_url, save_path="temp.pdf"):
    """
    Downloads a PDF from a given URL and saves it locally.
    """
    try:
        logging.info(f"📥 Downloading PDF from: {pdf_url}")
        response = requests.get(pdf_url, stream=True)

        if response.status_code == 200:
            with open(save_path, "wb") as pdf_file:
                for chunk in response.iter_content(1024):
                    pdf_file.write(chunk)
            logging.info(f"✅ PDF downloaded successfully: {save_path}")
            return save_path
        else:
            logging.error(f"❌ Failed to download PDF. Status Code: {response.status_code}")
            return None

    except Exception as e:
        logging.error(f"❌ Error downloading PDF: {str(e)}")
        return None

def extract_text_from_readable_pdf(pdf_path):
    """
    Extracts text from a readable (non-scanned) PDF using PyMuPDF (fitz).
    """
    try:
        logging.info(f"📄 Extracting text from readable PDF: {pdf_path}")
        doc = fitz.open(pdf_path)
        text = ""

        for page in doc:
            text += page.get_text("text") + "\n\n"

        if len(text.strip()) > 0:
            logging.info("✅ Successfully extracted text from PDF (Readable PDF).")
            return text
        else:
            logging.warning("⚠️ No text found. PDF might be scanned.")
            return None

    except Exception as e:
        logging.error(f"❌ Error extracting text from readable PDF: {str(e)}")
        return None

def pdf_to_images(pdf_path):
    """
    Converts a PDF file into a list of image objects (one per page).
    """
    try:
        logging.info(f"📄 Converting PDF to images: {pdf_path}")
        images = convert_from_path(pdf_path)
        logging.info(f"✅ Converted PDF into {len(images)} pages.")
        return images
    except Exception as e:
        logging.error(f"❌ Error converting PDF to images: {str(e)}")
        return None

def image_to_base64(image):
    """
    Converts a PIL image to a Base64-encoded string.
    """
    try:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception as e:
        logging.error(f"❌ Error encoding image to Base64: {str(e)}")
        return None

def extract_text_from_scanned_pdf(pdf_path):
    """
    Extracts text from a scanned (non-readable) PDF using Together AI Vision API.
    """
    try:
        images = pdf_to_images(pdf_path)
        if not images:
            logging.error("❌ No images extracted from PDF.")
            return None

        extracted_text = ""

        headers = {
            "Authorization": f"Bearer {TOGETHER_VISION_API_KEY}",
            "Content-Type": "application/json"
        }

        for idx, image in enumerate(images):
            logging.info(f"📄 Processing page {idx + 1}/{len(images)}")

            image_base64 = image_to_base64(image)
            if not image_base64:
                logging.warning(f"⚠️ Skipping page {idx + 1} due to encoding issue.")
                continue

            payload = {
                "model": TOGETHER_VISION_MODEL,
                "prompt": "Extract all readable text from this document page.",
                "image_base64": image_base64,
                "max_tokens": 500
            }

            response = requests.post(TOGETHER_VISION_API_URL, json=payload, headers=headers)

            try:
                response_json = response.json()
            except Exception as e:
                logging.error(f"❌ Failed to parse JSON response for page {idx + 1}: {str(e)}")
                continue

            logging.info(f"🔎 Full API Response for Page {idx + 1}: {response_json}")

            if response.status_code == 200:
                page_text = response_json.get("output", "").strip()
                if not page_text:
                    logging.warning(f"⚠️ No text extracted from page {idx + 1}.")
                    continue

                extracted_text += f"\n\n[Page {idx + 1}]\n{page_text}"
                logging.info(f"✅ Extracted text from page {idx + 1}: {page_text[:100]}...")

            else:
                logging.error(f"❌ API Call Failed for page {idx + 1}: {response.status_code} | {response.text}")

        return extracted_text if extracted_text else None

    except Exception as e:
        logging.error(f"❌ Exception in extract_text_from_scanned_pdf: {str(e)}")
        logging.error(traceback.format_exc())
        return None

def extract_text_from_pdf_url(pdf_url):
    """
    Extracts text from a PDF document via a URL.
    - If the PDF is readable, extracts text directly.
    - If the PDF is scanned, extracts text using Together AI Vision API.
    """

    print("Started extraction ::: ")

    try:
        pdf_path = download_pdf(pdf_url)
        if not pdf_path:
            return None

        print("Downloaded PDF ::: " , pdf_path)

        # Try extracting text from readable PDFs
        extracted_text = extract_text_from_readable_pdf(pdf_path)

        print("Extracted Text ::: " , extracted_text)

        if extracted_text:
            logging.info("✅ Using extracted text from readable PDF.")
            return extracted_text

        # If the PDF is not readable, use Together AI Vision API
        logging.warning("⚠️ No text found in PDF. Processing as scanned document.")
        extracted_text = extract_text_from_scanned_pdf(pdf_path)

        return extracted_text

    except Exception as e:
        logging.error(f"❌ Exception in extract_text_from_pdf_url: {str(e)}")
        logging.error(traceback.format_exc())
        return None


#url = "https://api.sci.gov.in/supremecourt/2023/3848/3848_2023_8_1501_58087_Judgement_19-Dec-2024.pdf"
#text = extract_text_from_pdf_url(url)