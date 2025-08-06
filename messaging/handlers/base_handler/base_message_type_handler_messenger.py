from messaging.models import PLATFORM
from messaging.utils import facebook_api
from .base_message_type_handler import BaseMessageTypeHandler
from business.models.integrations import FacebookIntegration

class BaseMessageTypeHandlerMessenger(BaseMessageTypeHandler):
    PLATFORM = PLATFORM.FACEBOOK

    def __init__(self):
        super().__init__()
        self.messenger_media_url = None
        self.messenger_media_file = None

    def send_platform_message(self, recipient: str, text: str) -> None:
        try:
            facebook_integration = FacebookIntegration.objects.get(user=self.user)
            access_token = facebook_integration.access_token
            facebook_api.send_message(recipient, text, access_token)
        except FacebookIntegration.DoesNotExist:
            print(f"ERROR: FacebookIntegration not found for user {self.user.email}. Cannot send message.")
        except Exception as e:
            print(f"ERROR sending message via Facebook API: {e}")



# from abc import ABC, abstractmethod
# from typing import Dict, Optional
# from chatbot.langgraph.chat_agent import ChatAgent

# # from chatbot.services.llm.agents import ChatAgent
# from chatbot.utils import ChatBotUtil
# from messaging.models.conversation import Conversation
# from messaging.models.user import SocialMediaUser
# from messaging.services import conversation_service, socialuser_service, whatsapp_service
# from messaging.services.chat_message_service import ChatMessageService
# from messaging.models import SENDER_CHOICES, PLATFORM
# from messaging.utils import facebook_api

# from asgiref.sync import async_to_sync

# class BaseMessageTypeHandlerMessenger(ABC):
#     def __init__(self):
#         self.user = None
#         self.socialuser = None
#         self.conversation = None
#         self.sender = None # Messenger sender ID
#         self.replier = None # 'ai' or 'business'
#         self.message = None
#         self.media_type = None
#         self.media_id = None
#         self.contacts = []
#         self.name = None
#         self.reply_message_for_socialuser = None
#         self.messenger_media_url = None
#         self.messenger_media_file = None

#     def set_socialuser_conversation(self):
#         socialuser = socialuser_service.get_or_create_socialuser(social_media_id=self.sender, platform=PLATFORM.FACEBOOK)
#         conversation = conversation_service.get_or_create_conversation(user=self.user, socialuser=socialuser )

#         self.socialuser = socialuser
#         self.conversation = conversation

#     @abstractmethod
#     def extract_fields(self, message: Dict)-> None:
#         """
#         Extract and set values from the raw message dict.
#         Each subclass implements its own parsing logic here.
#         """
#         pass

#     def send_platform_message(self, recipient: str, text: str) -> None:
#         facebook_api.send_message(recipient, text)

#     def  generate_auto_reply(self) -> Optional[str]:
#         """Subclasses can override this to add AI or business logic"""
#         # return ChatBotUtil.chat_with_gemini(prompt=self.message).text
#         agent = ChatAgent(user=self.user, conversation=self.conversation)
#         ai_response = async_to_sync(agent.get_response)(self.message)
#         return ai_response
    
#     def should_auto_reply(self) -> bool:
#         """Override in subclasses if auto-reply should be skipped."""
#         return False

#     def handle_message_from_customer(self):
#         """Process the message received from a customer."""
#         # i have to remember the sender here is different from self.sender because self.sender is a whatsapp id, here sender is the filed of Chatmessage Model
#         ChatMessageService.create_message(
#             conversation=self.conversation,
#             sender= SENDER_CHOICES.CUSTOMER,
#             message=self.message, 
#             media_type=self.media_type, 
#             media_id=self.media_id,
#             contacts=self.contacts,
#             messenger_media_url=self.messenger_media_url,
#             messenger_media_file=self.messenger_media_file
#         )
        

 
#     def handle_bot_or_businessman_reply(self):
#         """Process the reply from AI or a business user."""
#         if not self.reply_message_for_socialuser:
#             return  # Avoid sending blank reply

#         ChatMessageService.create_message(
#             conversation=self.conversation, 
#             sender=self.replier, 
#             message=self.reply_message_for_socialuser, 
#         )
#         self.send_platform_message(self.sender, self.reply_message_for_socialuser)



#     def handle(self, message: Dict, sender: str, message_type: str, name: Optional[str] = None, user = None):
#         self.sender = sender
#         self.media_type = message_type
#         self.name = name
#         self.user = user

#         self.extract_fields(message=message)
#         self.set_socialuser_conversation()
#         self.handle_message_from_customer()

#         if self.should_auto_reply() and self.conversation.auto_reply:
#             self.reply_message_for_socialuser = self.generate_auto_reply()
#             self.replier = SENDER_CHOICES.AI

#         self.handle_bot_or_businessman_reply()


        

