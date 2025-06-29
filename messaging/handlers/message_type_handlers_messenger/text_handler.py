from typing import Dict

from messaging.handlers.base_handler import BaseMessageTypeHandlerMessenger


class TextMessageHandler(BaseMessageTypeHandlerMessenger):
    def extract_fields(self, message: Dict)-> None:
        self.message = message['text']

    def should_auto_reply(self) -> bool:
        return True    
    