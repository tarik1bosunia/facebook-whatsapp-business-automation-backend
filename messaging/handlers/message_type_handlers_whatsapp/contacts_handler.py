from typing import Dict

from messaging.handlers.base_handler import BaseMessageTypeHandler
from messaging.models import SENDER_CHOICES
class ContactsMessageHandler(BaseMessageTypeHandler):
    def extract_fields(self, message: Dict)-> None:
        contacts_data = message.get("contacts", [])

        if not contacts_data:
            self.message = "No contacts received"
            self.contacts = []
            return

        self.contacts  = [
            {
                "name": contact.get("name", {}).get("formatted_name", ''),
                "phones": [
                    phone.get("phone") for phone in contact.get("phones", []) if phone.get("phone")
                ]
            }
            for contact in contacts_data
        ]

        self.message = f"{len(self.contacts)} contact(s) received"
        self.reply_message_for_user = "Thanks for sharing the contacts"
        self.replier = SENDER_CHOICES.BUSINESS


    def should_auto_reply(self) -> bool:
        return False   


