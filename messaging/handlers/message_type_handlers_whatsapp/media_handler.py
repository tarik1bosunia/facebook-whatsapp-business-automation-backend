from typing import Dict

from messaging.handlers.base_handler import BaseMessageTypeHandlerWhatsApp
from messaging.models import SENDER_CHOICES

class MediaMessageHandler(BaseMessageTypeHandlerWhatsApp):
    def extract_fields(self, message: Dict)-> None:
        self.media_id = message[self.media_type]['id']
        self.message = message[self.media_type].get('caption', 'No caption')
        self.reply_message_for_socialuser = f"Thanks for the {self.media_type}! We'll process it soon."
        self.replier = SENDER_CHOICES.BUSINESS


    def should_auto_reply(self) -> bool:
        return False    

