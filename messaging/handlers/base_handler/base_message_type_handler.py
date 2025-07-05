from abc import ABC, abstractmethod
from typing import Dict, Optional

from chatbot.utils import ChatBotUtil
from messaging.models.conversation import Conversation
from messaging.models.user import SocialMediaUser
from messaging.services import conversation_service, socialuser_service, whatsapp_service
from messaging.services.chat_message_service import ChatMessageService
from messaging.models import SENDER_CHOICES, PLATFORM

class BaseMessageTypeHandler(ABC):
    def __init__(self):
        self.user = None
        self.socialuser = None
        self.conversation = None
        self.sender = None # WhatsApp sender ID
        self.replier = None # 'ai' or 'business'
        self.message = None
        self.media_type = None
        self.media_id = None
        self.contacts = []
        self.name = None
        self.reply_message_for_user = None

    def set_socialuser_conversation(self):
        self.socialuser = socialuser_service.get_or_create_socialuser(social_media_id=self.sender, platform=PLATFORM.WHATSAPP)
        self.conversation = conversation_service.get_or_create_conversation(user=self.user, socialuser=self.socialuser )
        #  TODO: I have to update the name of the social media user

        # if self.name and socialuser.name != self.name:
        #     socialuser.name = self.name
        #     socialuser.save()


    @abstractmethod
    def extract_fields(self, message: Dict)-> None:
        """
        Extract and set values from the raw message dict.
        Each subclass implements its own parsing logic here.
        """
        pass

    def generate_auto_reply(self) -> Optional[str]:
        """Subclasses can override this to add AI or business logic"""
        return ChatBotUtil.chat_with_gemini(prompt=self.message).text
    
    def should_auto_reply(self) -> bool:
        """Override in subclasses if auto-reply should be skipped."""
        return False

    def handle_message_from_customer(self):
        """Process the message received from a customer."""
        # i have to remember the sender here is different from self.sender because self.sender is a whatsapp id, here sender is the filed of Chatmessage Model
        ChatMessageService.create_message(
            conversation=self.conversation,
            sender= SENDER_CHOICES.CUSTOMER,
            message=self.message, 
            media_type=self.media_type, 
            media_id=self.media_id,
            contacts=self.contacts
        )
        

 
    def handle_bot_or_businessman_reply(self):
        """Process the reply from AI or a business user."""
        if not self.reply_message_for_socialuser:
            return  # Avoid sending blank reply

        ChatMessageService.create_message(
            conversation=self.conversation, 
            sender=self.replier, 
            message=self.reply_message_for_socialuser, 
        )

        whatsapp_service.WhatsAppService().send_text_message(
            phone_number=self.sender,
            message=self.reply_message_for_socialuser
        )


    def handle(self, message: Dict, sender: str, message_type: str, name: Optional[str] = None, user= None):
        self.sender = sender
        self.media_type = message_type
        self.name = name
        self.user = user

        self.extract_fields(message=message)
        self.set_socialuser_conversation()
        self.handle_message_from_customer()

        if self.should_auto_reply() and self.conversation.auto_reply:
            self.reply_message_for_socialuser = self.generate_auto_reply()
            self.replier = SENDER_CHOICES.AI

        self.handle_bot_or_businessman_reply()
