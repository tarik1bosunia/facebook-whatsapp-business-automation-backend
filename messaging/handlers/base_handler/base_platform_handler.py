

import json
import logging
from typing import Dict, Optional
from django.http import HttpRequest, JsonResponse

from .base_webhook_handler import BaseWebHookHandler

logger = logging.getLogger(__name__)


class BasePlatformHandler(BaseWebHookHandler):
    """
    Base class for Messenger and WhatsApp webhook handlers.
    Subclasses define:
      - HANDLERS (dict)
      - validate_object_type (method)
      - extract_user_and_message (method)
    """

    HANDLERS: Dict[str, type] = {}

    # -------------- PUBLIC ENTRYPOINT --------------
    def _handle_incoming_message(self, request: HttpRequest) -> JsonResponse:
        try:
            data = self._validate_request(request)
            self._process_entries(data.get("entry", []))
            return JsonResponse({"status": "success"}, status=200)
        except Exception as e:
            return self._handle_error(e)

    # -------------- PROCESSING --------------
    def _process_entries(self, entries: list) -> None:
        """Iterate entries and delegate to subclass method."""
        for entry in entries:
            try:
                self._process_entry(entry)
            except Exception as e:
                logger.error(f"Failed to process entry: {str(e)}", exc_info=True)

    def _process_entry(self, entry: Dict) -> None:
        """Must be implemented by subclass (Messenger/WhatsApp)."""
        raise NotImplementedError

    def _route_message(self, message: Dict, sender: str, message_type: str, name: Optional[str] = None, user=None):
        """Dispatch message to appropriate handler."""
        handler_class = self.HANDLERS.get(message_type, self.HANDLERS.get("unsupported"))
        if not handler_class:
            raise ValueError(f"No handler for message type: {message_type}")

        handler = handler_class()
        handler.handle(message=message, sender=sender, message_type=message_type, name=name, user=user)

    # -------------- VALIDATION --------------
    def _validate_request(self, request: HttpRequest) -> Dict:
        """Validate JSON and platform type (delegated to subclass)."""
        if not request.body:
            raise ValueError("Empty request body")

        data = json.loads(request.body)
        self._validate_object_type(data)  # delegate to subclass
        return data

    def _validate_object_type(self, data: Dict):
        """Subclasses override to check 'object' value."""
        raise NotImplementedError

    # -------------- ERROR HANDLING --------------
    def _handle_error(self, error: Exception) -> JsonResponse:
        if isinstance(error, json.JSONDecodeError):
            logger.error(f"JSON decode error: {str(error)}")
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        elif isinstance(error, ValueError):
            logger.warning(str(error))
            return JsonResponse({"error": str(error)}, status=400)
        else:
            logger.error(f"Message processing error: {str(error)}", exc_info=True)
            return JsonResponse({"error": "Message processing failed"}, status=500)
