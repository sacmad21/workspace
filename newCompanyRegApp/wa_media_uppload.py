from flask import Flask, request, jsonify
import requests
import os
from io import BytesIO

app = Flask(__name__)

@app.route('/api/whatsapp/media/upload', methods=['POST'])
def upload_media():
    if request.method == 'POST':
        try:
            # Extract the file and mimeType from the request body
            data = request.get_json()
            file = data.get('file')  # Expecting base64 or binary data
            mime_type = data.get('mimeType')

            if not file or not mime_type:
                return jsonify({"error": "Missing file or mimeType in request body."}), 400

            # WhatsApp Cloud API URL
            upload_url = f"{os.getenv('WHATSAPP_CLOUD_API_URL')}/media"

            # Prepare the form data
            form_data = {
                'messaging_product': 'whatsapp',
            }

            # Convert the file to a binary stream
            file_data = BytesIO(file.encode('latin1')) if isinstance(file, str) else BytesIO(file)
            files = {
                'file': ('file', file_data, mime_type)
            }

            # Send the request to WhatsApp Cloud API
            headers = {
                'Authorization': f"Bearer {os.getenv('WHATSAPP_CLOUD_API_TOKEN')}"
            }

            response = requests.post(upload_url, data=form_data, files=files, headers=headers)

            # Handle response
            if response.status_code == 200:
                return jsonify(response.json()), 200
            else:
                return jsonify({"error": response.json()}), response.status_code

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    else:
        return jsonify({"error": f"Method {request.method} Not Allowed"}), 405

if __name__ == '__main__':
    app.run(debug=True)
