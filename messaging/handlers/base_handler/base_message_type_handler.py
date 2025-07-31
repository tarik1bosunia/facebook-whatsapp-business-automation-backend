from abc import ABC, abstractmethod
from typing import Dict, Optional
from chatbot.langgraph.chat_agent import ChatAgent
from messaging.services import conversation_service, socialuser_service
from messaging.services.chat_message_service import ChatMessageService
from messaging.models import SENDER_CHOICES
from asgiref.sync import async_to_sync

class BaseMessageTypeHandler(ABC):
    """
    Common base handler for all message types (WhatsApp, Messenger, etc.).
    Subclasses must implement platform-specific parts.
    """

    PLATFORM = None  # Must be set in subclasses

    def __init__(self):
        self.user = None
        self.socialuser = None
        self.conversation = None
        self.sender = None   # platform-specific sender ID
        self.replier = None  # 'ai' or 'business'
        self.message = None
        self.media_type = None
        self.media_id = None
        self.contacts = []
        self.name = None
        self.reply_message_for_socialuser = None

        

    @abstractmethod
    def send_platform_message(self, recipient: str, text: str) -> None:
        """Send reply to customer via platform API (WhatsApp, Messenger, etc.)."""
        pass

    @abstractmethod
    def extract_fields(self, message: Dict) -> None:
        """
        Extract and set values from the raw message dict.
        Each subclass implements its own parsing logic here.
        """
        pass

    def set_socialuser_conversation(self):
        self.socialuser = socialuser_service.get_or_create_socialuser(
            social_media_id=self.sender, platform=self.PLATFORM
        )
        self.conversation = conversation_service.get_or_create_conversation(
            user=self.user, socialuser=self.socialuser
        )

    def generate_auto_reply(self) -> Optional[str]:
        agent = ChatAgent(user=self.user, conversation=self.conversation)
        return async_to_sync(agent.get_response)(self.message)

    def should_auto_reply(self) -> bool:
        return False

    def handle_message_from_customer(self):
        ChatMessageService.create_message(
            conversation=self.conversation,
            sender=SENDER_CHOICES.CUSTOMER,
            message=self.message,
            media_type=self.media_type,
            media_id=self.media_id,
            contacts=self.contacts
        )

    def handle_bot_or_businessman_reply(self):
        if not self.reply_message_for_socialuser:
            return

        ChatMessageService.create_message(
            conversation=self.conversation,
            sender=self.replier,
            message=self.reply_message_for_socialuser,
        )

        self.send_platform_message(self.sender, self.reply_message_for_socialuser)

    def handle(self, message: Dict, sender: str, message_type: str, name: Optional[str] = None, user=None):
        self.sender = sender
        self.media_type = message_type
        self.name = name
        self.user = user

        self.extract_fields(message)
        self.set_socialuser_conversation()
        self.handle_message_from_customer()

        if self.should_auto_reply() and self.conversation.auto_reply:
            self.reply_message_for_socialuser = self.generate_auto_reply()
            self.replier = SENDER_CHOICES.AI

        self.handle_bot_or_businessman_reply()
