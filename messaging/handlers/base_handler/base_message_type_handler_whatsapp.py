from messaging.models import PLATFORM
from messaging.services import whatsapp_service
from .base_message_type_handler import BaseMessageTypeHandler

class BaseMessageTypeHandlerWhatsApp(BaseMessageTypeHandler):
    PLATFORM = PLATFORM.WHATSAPP

    def send_platform_message(self, recipient: str, text: str) -> None:
        whatsapp_service.WhatsAppService().send_text_message(
            phone_number=recipient,
            message=text
        )




    