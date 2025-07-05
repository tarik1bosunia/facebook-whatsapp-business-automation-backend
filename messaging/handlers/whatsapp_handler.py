from typing import Dict, Optional
from django.conf import settings
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    JsonResponse
)
import json
import logging


from ..exceptions import WebhookVerificationError
from .base_handler import BaseWebHookHandler
logger = logging.getLogger(__name__)

from .message_type_handlers_whatsapp import (
    TextMessageHandler,
    MediaMessageHandler,
    TemplateMessageHandler,
    ContactsMessageHandler,
    UnsupportedMessageHandler
)
from business.models import WhatsAppIntegration

class WhatsAppHandler(BaseWebHookHandler):
    def __init__(self):
        self.handlers = {
            'text': TextMessageHandler,
            'image': MediaMessageHandler,
            'audio': MediaMessageHandler,
            'video': MediaMessageHandler,
            'document': MediaMessageHandler,
            'template': TemplateMessageHandler,
            'contacts': ContactsMessageHandler,
            'unsupported': UnsupportedMessageHandler, 
        }


    def _handle_incoming_message(self, request: HttpRequest) -> JsonResponse:
        """Process incoming message payload"""
        try:
            data = self._validate_request(request)
            print("============================ REQUEST WHATSAPP ====================")
            print(json.loads(request.body))
            print("============================ REQUEST WHATSAPP ====================")
            self._process_entries(data.get('entry', []))
            return JsonResponse({'status': 'success'}, status=200)

        except Exception as e:
            return self._handle_error(e)

    def _process_entries(self, entries):
        """Process all entries in the webhook payload"""
        for entry in entries:
            try:
                self._process_entry(entry)
            except Exception as e:
                logger.error(f"Failed to process entry: {str(e)}", exc_info=True)
    def _process_entry(self, entry: Dict) -> None:
        """Process each entry in the webhook payload"""
        try:
            for change in entry.get('changes', []):
                
                if change.get('field') == 'messages':
                    self._process_message_change(change['value'])
        except Exception as e:
            logger.error(f"Entry processing failed: {str(e)}", exc_info=True)

    def _process_message_change(self, message_data: Dict) -> None:
        """Route message to appropriate handler"""
        metadata = message_data.get("metadata", {})
        messages = message_data.get('messages', [])
        contacts = message_data.get('contacts', [])
        phone_number_id = metadata.get("phone_number_id")
        if not phone_number_id:
            raise ValueError("Missing phone_number_id in metadata")
        
        integration = WhatsAppIntegration.objects.filter(platform_id=phone_number_id).first()
        if not integration:
            raise ValueError(f"No WhatsAppIntegration found for phone_number_id {phone_number_id}")
        
        self.user = integration.user

        if not messages:
            return
        
        if contacts:
            contact = contacts[0]  # Usually one contact per message
            name = contact.get('profile', {}).get('name')
            wa_id = contact.get('wa_id')

        message = messages[0]
        self._route_message(message, name)

    def _route_message(self, message: Dict, name: Optional[str] = None) -> None:
        """Route message to the correct handler based on type"""
        sender = message.get('from')
        message_type = message.get('type')

        if not sender or not message_type:
            raise ValueError("Incomplete message data")

        handler_class = self.handlers.get(message_type)
        if not handler_class:
            handler_class = self.handlers.get('unsupported')

        handler = handler_class()
        handler.handle(message=message, sender=sender, message_type=message_type, name=name, user=self.user)


    def _validate_request(self, request):
        """Validate the incoming request structure"""
        if not request.body:
            raise ValueError("Empty request body")

        data = json.loads(request.body)

        if data.get('object') != 'whatsapp_business_account':
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