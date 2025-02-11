from base_state import BaseState
from common_state_functions import process_document_upload, guide_user_for_document

class UploadDocuments(BaseState):
    """Handles document uploads with validation, metadata extraction, and summarization."""

    def handle(self, user_message, phone_number, document=None):
        """
        Guides the user through the document upload process.
        Ensures all required documents are collected before moving forward.
        """
        if user_message.lower() == "done":
            send_whatsapp_message(phone_number, "✅ All documents uploaded successfully. Moving to the next step.")
            self.state_manager.transition("awaiting_next_action")
            return

        if user_message.lower() == "skip":
            send_whatsapp_message(phone_number, "⏭ Skipping this document. Moving to the next one.")
            guide_user_for_document(self.state_manager, phone_number)
            return

        if not document:
            guide_user_for_document(self.state_manager, phone_number)
            return

        process_document_upload(self.state_manager, phone_number, document)
