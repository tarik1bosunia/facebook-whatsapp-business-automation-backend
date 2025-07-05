
import json

from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse

from chatbot.utils import ChatBotUtil

from .base_handler import BaseWebHookHandler
from ..services import socialuser_service, conversation_service, websocket_service
from ..utils import facebook_api

import logging
from ..exceptions import WebhookVerificationError
logger = logging.getLogger(__name__)
from business.models import FacebookIntegration

from messaging.handlers.message_type_handlers_messenger import TextMessageHandler, AttachmentsMessageHandler

# TODO: need to handle all type of attachments(image, audio, video, document) also
class MessengerHandler(BaseWebHookHandler):
    def __init__(self):

        self.handlers = {
            'text': TextMessageHandler,
            'attachments': AttachmentsMessageHandler,
            # 'image': MediaMessageHandler,
            # 'audio': MediaMessageHandler,
            # 'video': MediaMessageHandler,
            # 'document': MediaMessageHandler,
            # 'template': TemplateMessageHandler,
            # 'contacts': ContactsMessageHandler,
            # 'unsupported': UnsupportedMessageHandler, 
        }


    def _handle_incoming_message(self, request):
        try:
            data = self._validate_request(request=request)
            print("=========================== FACEBOOK DATA START =======================")
            print(data)
            print("=========================== FACEBOOK DATA END =======================")
            self._process_entries(data.get('entry', []))
            return JsonResponse({'status': 'ok'}, status=200)
        except Exception as e:
            return self._handle_error(e)

    def _process_entries(self, entries):
        for entry in entries:
            time = entry.get("time")
            facebook_page_id = entry.get("id")
            facebook_integration = FacebookIntegration.objects.get(platform_id=facebook_page_id)
            if not facebook_integration:
                print("no facebook integration found!")
                return
            self.user = facebook_integration.user

            print("FACEBOOK PAGE ID::", facebook_page_id)
            

            for event in entry.get('messaging', []):
                if event.get('message'):
                    self._handle_message_event(event)
                elif event.get('postback'):
                    self._handle_postback_event(event)

    def _handle_message_event(self, event):
        sender_id = event['sender']['id']
        message = event['message']
        print("MESSAGE ==================", message)

        # ============== NEW +++++++++++++++++++++++++
        if 'text' in message:
            message_type = 'text'
        if 'attachments' in message:
            message_type = "attachments"

        sender = sender_id
        name = "name..."
        handler_class = self.handlers.get(message_type)
        # if not handler_class:
        #     handler_class = self.handlers.get('unsupported')

        handler = handler_class()

        # TODO: may be need to pass user herer
        handler.handle(message=message, sender=sender, message_type=message_type, name=name, user=self.user)
        #  ============= NEW ++++++++++++++++++++++++

        # if 'text' in message:
        #     try:
        #         user = user_service.get_or_create_user(sender_id, platform='facebook')
        #         conversation = conversation_service.get_or_create_conversation(user)

        #         # Save incoming message
        #         user_message = message['text']
        #         websocket_service.message_from_outside_consumer(group_name=f'conversation_{conversation.id}', sender='customer', message=user_message)

        #         conversation_service.save_message(
        #             conversation=conversation,
        #             message=user_message,
        #             sender='customer'
        #         )

        #         # AUTO REPLY
        #         if conversation.auto_reply:

        #             gemini_response = ChatBotUtil.chat_with_gemini(prompt=user_message)

        #             facebook_api.send_message(sender_id, gemini_response.text)

        #             # TODO: websoket::  for message sent to frontend 
        #             websocket_service.message_from_outside_consumer(group_name=f'conversation_{conversation.id}', sender='ai', message=gemini_response.text)

        #             # Save bot response
        #             conversation_service.save_message(
        #                 conversation=conversation,
        #                 message=gemini_response.text,
        #                 sender='ai'
        #             )

        #     except Exception as e:
        #         print(f"Error processing message: {str(e)}")
        #         facebook_api.send_message(sender_id, "Sorry, I encountered an error")

        # TODO: handle attachments
        # if 'attachments' in message:
        #     for attachment in message['attachments']:
        #         attachment_type = attachment.get('type')
        #         payload = attachment.get('payload', {})
        #         url = payload.get('url')

        #         if attachment_type == 'audio' and url:
        #             # Handle audio message
        #             print(f"Audio message received! URL: {url}")
        #             # Optionally: save to DB, send to frontend, trigger transcription, etc.
    def _handle_postback_event(self, event):
        sender_id = event['sender']['id']
        payload = event['postback']['payload']

        try:
            socialuser= socialuser_service.get_or_create_socialuser(sender_id)
            conversation = conversation_service.get_or_create_conversation(socialuser)

            # Save postback as message
            conversation_service.save_message(
                conversation=conversation,
                message=f"[POSTBACK] {payload}",
                sender='customer'
            )

            response_text = f"You selected: {payload}"
            facebook_api.send_message(sender_id, response_text)

            # Save bot response
            conversation_service.save_message(
                conversation=conversation,
                message=response_text,
                sender='ai'
            )
        except Exception as e:
            print(f"Error processing postback: {str(e)}")
            facebook_api.send_message(sender_id, "Sorry, I couldn't process your selection")
   
    def _validate_request(self, request):
        """Validate the incoming request structure"""
        if not request.body:
            raise ValueError("Empty request body")

        data = json.loads(request.body)

        if data.get('object') != 'page':
            raise ValueError("Invalid object received")

        return data
    
    def _handle_error(self, error: Exception) -> JsonResponse:
        """Handle different types of errors appropriately"""
        if isinstance(error, json.JSONDecodeError):
            logger.error(f"JSON decode error: {str(error)}")
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        elif isinstance(error, ValueError):
            logger.warning(str(error))
            return JsonResponse({"error": str(error)}, status=400)
        else:
            logger.error(f"Message processing error: {str(error)}", exc_info=True)
            return JsonResponse(
                {"error": "Message processing failed"},
                status=500
            )