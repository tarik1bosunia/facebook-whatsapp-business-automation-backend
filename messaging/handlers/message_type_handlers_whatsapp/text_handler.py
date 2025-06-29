from typing import Dict
from messaging.handlers.base_handler import BaseMessageTypeHandler


class TextMessageHandler(BaseMessageTypeHandler):
    def extract_fields(self, message: Dict)-> None:
        self.message = message['text']['body']

    def should_auto_reply(self) -> bool:
        return True    
    