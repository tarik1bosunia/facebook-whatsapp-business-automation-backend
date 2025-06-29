from typing import Dict

from messaging.handlers.base_handler import BaseMessageTypeHandlerMessenger
from messaging.models import SENDER_CHOICES
from messaging.utils.save_image_from_url import save_image_from_url_to_field

class AttachmentsMessageHandler(BaseMessageTypeHandlerMessenger):
    def extract_fields(self, message: Dict)-> None:
        # self.media_id = message[self.media_type]['id']
        # self.message = message[self.media_type].get('caption', 'No caption')


        print("MESSSAGE =======================")
        print(message)
        print("MESSSAGE =======================")

        for attachment in message['attachments']:
            attachment_type = attachment.get('type')
            payload = attachment.get('payload', {})
            url = payload.get('url')
            self.messenger_media_url = url
            if attachment_type == 'image' and url:
                self.media_type = 'image'
                print(f"Image message received...! URL :: ", url)

            elif attachment_type == 'video' and url:
                self.media_type = 'video'

            elif attachment_type == 'audio' and url:
                self.media_type = 'audio'
            elif attachment_type == 'file' and url:
                self.media_type = 'document'    



        self.reply_message_for_socialuser = f"Thanks for the {self.media_type}! We'll process it soon."
        self.replier = SENDER_CHOICES.BUSINESS

    def should_auto_reply(self) -> bool:
        return False    
