import logging

logger = logging.getLogger(__name__)

class UnsupportedMessageHandler:
    def handle(self, message: dict, sender: str, message_type: str, name=None):
        logger.warning(f"Received unsupported message type '{message_type}' from {sender}. Message ID: {message.get('id')}")

        # Optional: You can save this message info to DB or send a reply to socialuser
        # Example: send text reply saying unsupported message type
        # whatsapp_service.WhatsAppService().send_text_message(
        #     phone_number=sender,
        #     message=f"Sorry, we cannot process messages of type '{message_type}' yet."
        # )
