
# TODO: I have to study about template messages and session messages then need to modify it

import logging
from typing import Dict

logger = logging.getLogger(__name__)

class TemplateMessageHandler:
    def handle(self, message: Dict, sender: str, message_type: str, name=None):
        """Process template message responses"""
        template_name = message['template']['name']
        logger.info(f"Template response from {sender}: {template_name}")

        # TODO: Handle different template responses
        # Example: Handle appointment confirmation
        if template_name == "appointment_confirmation":
            self._handle_appointment_confirmation(message, sender)

    def _handle_appointment_confirmation(self, message: Dict, sender: str):
        """Example: Process appointment confirmation"""
        status = message['template']['button_response']['text']
        logger.info(f"Appointment status: {status} from {sender}")