import logging
from typing import Any, Dict, List, Optional
from channels.db import database_sync_to_async
from django.core.exceptions import ValidationError

from messaging.models.conversation import Conversation
from messaging.services import conversation_service, whatsapp_service
from messaging.utils import facebook_api
from messaging.validators import validate_message_content
from business.models.integrations import FacebookIntegration

logger = logging.getLogger(__name__)

class MessageHandlerService:
    def __init__(self, user):
        self.user = user

    async def process_and_send_message(self, payload: Dict[str, Any]) -> Optional[Conversation]:
        """
        Validates, saves, and sends a message to the appropriate platform.
        Returns the conversation object if successful, None otherwise.
        """
        try:
            # Validate payload
            if not self.validate_message_payload(payload):
                logger.error("Invalid message payload received.")
                return None

            conversation_id = payload.get('conversation_id')
            message_text = payload.get('text')
            logger.info(f"Processing message for conversation {conversation_id}")

            # Get conversation from database
            conversation = await self._get_conversation(conversation_id)
            if not conversation:
                logger.error(f"Conversation {conversation_id} not found.")
                return None

            # Save message to database
            await self._save_message_to_db(
                conversation=conversation,
                message=message_text,
                sender='business',
                media_id=payload.get('media_id'),
                media_type=payload.get('media_type'),
                media_url=payload.get('media_url'),
                contacts=payload.get('contacts', [])
            )

            # Fetch platform and social ID safely
            platform, social_media_id = await self._get_conversation_platform_and_id(conversation)

            await self._send_platform_message(platform, social_media_id, message_text)

            return conversation

        except ValidationError as e:
            logger.error(f"Message validation failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error in process_and_send_message: {str(e)}")
            return None

    def validate_message_payload(self, payload: Dict[str, Any]) -> bool:
        """Validate incoming message payload."""
        if not payload.get('conversation_id'):
            logger.error("Missing conversation_id in payload")
            return False

        try:
            message_text = payload.get('text')
            if not message_text:
                logger.error("Empty message text")
                return False

            validate_message_content(message_text)
            return True
        except ValidationError as e:
            logger.error(f"Message validation failed: {str(e)}")
            return False

    @database_sync_to_async
    def _get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation from database."""
        try:
            return Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error fetching conversation: {str(e)}")
            return None

    @database_sync_to_async
    def _save_message_to_db(self, conversation: Conversation, message: str, sender: str,
                             media_id: Optional[str] = None, media_url: Optional[str] = None,
                             media_type: Optional[str] = None, contacts: Optional[List[Dict[str, Any]]] = None):
        """Save message to database with additional media info."""
        try:
            conversation_service.save_message(
                conversation=conversation,
                message=message,
                sender=sender,
                media_id=media_id,
                media_url=media_url,
                media_type=media_type,
                contacts=contacts
            )
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            raise

    @database_sync_to_async
    def _get_conversation_platform_and_id(self, conversation: Conversation) -> tuple[str, str]:
        """Get platform and social ID from conversation."""
        try:
            socialuser = conversation.socialuser
            return socialuser.platform, socialuser.social_media_id
        except Exception as e:
            logger.error(f"Error getting platform info: {str(e)}")
            raise

    async def _send_platform_message(self, platform: str, recipient_id: str, message: str):
        """Send message to the appropriate platform."""
        try:
            if platform == 'facebook':
                await self._send_facebook_message(recipient_id, message)
            elif platform == 'whatsapp':
                await self._send_whatsapp_message(recipient_id, message)
            else:
                logger.warning(f"Unsupported platform: {platform}")
        except Exception as e:
            logger.error(f"Error sending {platform} message: {str(e)}")
            raise

    @database_sync_to_async
    def _send_facebook_message(self, social_media_id: str, message: str):
        """Send message via Facebook API."""
        try:
            facebook_integration = FacebookIntegration.objects.get(user=self.user)
            access_token = facebook_integration.access_token
            facebook_api.send_message(social_media_id, message, access_token)
        except FacebookIntegration.DoesNotExist:
            logger.error(f"FacebookIntegration not found for user {self.user.email}. Cannot send message.")
            raise
        except Exception as e:
            logger.error(f"Facebook API error: {str(e)}")
            raise

    @database_sync_to_async
    def _send_whatsapp_message(self, phone_number: str, message: str):
        """Send message via WhatsApp API."""
        try:
            whatsapp_service.WhatsAppService().send_text_message(
                phone_number=phone_number,
                message=message,
            )
        except Exception as e:
            logger.error(f"WhatsApp API error: {str(e)}")
            raise