from typing import Any, Dict, Optional
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json
from datetime import datetime, timedelta
from enum import Enum

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError

from messaging.models.conversation import Conversation
from messaging.services import conversation_service, whatsapp_service
from messaging.utils import facebook_api
from messaging.validators import validate_message_content
from business.models.integrations import FacebookIntegration

import logging
logger = logging.getLogger(__name__)


CLOSE_CODE_UNAUTHENTICATED = 4001
CLOSE_CODE_HEARTBEAT_TIMEOUT = 4002
CLOSE_CODE_CONNECTION_SETUP_FAILED = 4003


class MessageTypes(Enum):
    HEARTBEAT = "heartbeat"
    HANDSHAKE = "handshake"
    NEW_MESSAGE = "new_message"
    NOTIFICATION = "notification"
    ACKNOWLEDGMENT = "acknowledgment"
    ERROR = "error"


class ChatAsyncJsonWebsocketConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_heartbeat = None
        self.heartbeat_timeout = 40  # seconds
        self.heartbeat_interval = 30  # seconds
        self.user = None
        self.group_name = None
        self.connected_at = None
        self.message_counter = 0

    async def connect(self):
        """Handle new WebSocket connection."""
        print('======================== WEBSOKET  connected... ============')
        self.connected_at = datetime.now()
        # logger.info(f"New WebSocket connection attempt: {self.scope}")
        # print('channel layer::', self.channel_layer)

        # Update channel name immediately upon connection
        print('channel name::', self.channel_name)

        # Get authenticated user from scope (set by JWTAuthMiddleware)
        self.user = self.scope.get("user")

        if isinstance(self.user, AnonymousUser):
            logger.warning("Unauthenticated connection attempt")
            await self.close(code=CLOSE_CODE_UNAUTHENTICATED)
            return

        logger.info(f"Authenticated connection for user {self.user.id}")
        self.group_name = f'user_{self.user.id}_chat'

        try:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            self.last_heartbeat = datetime.now()

        # Send initial handshake with user info
            await self.send_json({
                "type": MessageTypes.HANDSHAKE.value,
                "status": "authenticated",
                "user_id": str(self.user.id),
                "timestamp": datetime.now().isoformat(),
                "heartbeat_interval": self.heartbeat_interval
            })

        except Exception as e:
            logger.error(f"Connection setup failed: {str(e)}")
            await self.close(code=CLOSE_CODE_CONNECTION_SETUP_FAILED)

    async def receive_json(self, content, **kwargs):
        """Handle incoming WebSocket messages."""
        try:
            if not self.user or isinstance(self.user, AnonymousUser):
                await self.close(code=CLOSE_CODE_UNAUTHENTICATED)
                return

            logger.debug(f"Received message: {content}")

            message_type = content.get("type")

            if message_type == MessageTypes.HEARTBEAT.value:
                self.last_heartbeat = datetime.now()
                print("Heartbeat received")
                await self.send_heartbeat_response()
                return

            if message_type == MessageTypes.HANDSHAKE.value:
                await self.handle_handshake(content)
                return

            if message_type == MessageTypes.NEW_MESSAGE.value:
                payload = content.get("payload")
                if payload:
                    await self.handle_message(payload)

                    # Send acknowledgment
                    await self.send_json({
                        "type": MessageTypes.ACKNOWLEDGMENT.value,
                        "message_id": payload.get("id"),
                        "status": "received",
                        "timestamp": datetime.now().isoformat()
                    })

            # Handle regular messages
            await self.check_connection_health()

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.send_json({
                "type": MessageTypes.ERROR.value,
                "error": "message_processing_error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        logger.info(f"Disconnecting with code {close_code}")
        if hasattr(self, "group_name") and self.group_name:
            try:
                await self.channel_layer.group_discard(
                    self.group_name,
                    self.channel_name
                )
            except Exception as e:
                logger.error(f"Error during disconnect: {str(e)}")
        await super().disconnect(close_code)


    async def send_heartbeat_response(self):
        """Send heartbeat acknowledgment."""
        await self.send_json({
            "type": MessageTypes.HEARTBEAT.value,
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "next_expected_in": self.heartbeat_interval
        })

    async def handle_message(self, payload):
        """Process and broadcast chat messages."""
        try:
            # Validate payload
            if not self.validate_message_payload(payload):
                raise ValidationError("Invalid message payload")

            conversation_id = payload.get('conversation_id')
            message_text = payload.get('text')
            logger.info(
                f"Processing message for conversation {conversation_id}")

            # Get conversation from database
            conversation = await self.get_conversation(conversation_id)
            if not conversation:
                print(f"Conversation {conversation_id} not found")
                return

            # Save message to database
            await self.save_message_to_db(
                conversation=conversation,
                message=message_text,
                sender='business',
                media_id=payload.get('media_id'),
                media_type=payload.get('media_type'),
                media_url=payload.get('media_url')
                # contacts = payload.get('contacts', [])
            )

            # Fetch platform and social ID safely
            platform, social_media_id = await self.get_conversation_platform_and_id(conversation)

            await self.send_platform_message(platform, social_media_id, message_text)

            # Broadcast to group
            await self.broadcast_message(payload, conversation_id)

        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            raise

    async def send_platform_message(self, platform: str, recipient_id: str, message: str):
        """Send message to the appropriate platform."""
        try:
            if platform == 'facebook':
                await self.send_facebook_message(recipient_id, message)
            elif platform == 'whatsapp':
                await self.send_whatsapp_message(recipient_id, message)
            else:
                logger.warning(f"Unsupported platform: {platform}")
        except Exception as e:
            logger.error(f"Error sending {platform} message: {str(e)}")
            raise

    async def chat_message(self, event):
        """Handle incoming chat messages from the group."""
        print("====================== CHAT MESSAGE =========")
        # print("sender channel::", event.get("sender_channel"))
        if event.get("sender_channel") == self.channel_name:
            return  # Skip if this is the sender's channel
        print("sender channel::", event.get("sender_channel"))
        print("sender channel self::", self.channel_name)

        # Forward the message to the client as text
        # message = json.loads(event['message'])
        # conversation_id = message.pop('conversation_id', None)

        try:
            message = json.loads(event["message"])
            self.message_counter += 1
            await self.send_json({
                "type": MessageTypes.NEW_MESSAGE.value,
                "payload": {
                    **message,
                    "received_at": datetime.now().isoformat(),
                    "sequence_id": self.message_counter
                }
            })

        except json.JSONDecodeError as e:
            print(f"Error decoding message: {str(e)}")

        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")


    async def broadcast_message(self, payload: Dict[str, Any], conversation_id: str):
        """Broadcast message to all group members."""
        try:
            message_id = f"ws-{int(datetime.now().timestamp() * 1000)}"

            message_data = {
                "id": message_id,
                "text": payload.get('text'),
                "time": datetime.now().isoformat(),
                "sender": "business",
                "media_id": payload.get('media_id'),
                "media_url": payload.get('media_url'),
                "media_type": payload.get('media_type'),
                "contacts": payload.get('contacts', []),
            }

            print("channel name from broadcast self", self.channel_name)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat.message',
                    'message': json.dumps({
                        "conversation_id": str(conversation_id),
                        "message":message_data
                    }),
                    'sender_channel': self.channel_name
                }
            )
        except Exception as e:
            logger.error(f"Error broadcasting message: {str(e)}")
            raise

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

    async def check_connection_health(self):
        """Close connection if no heartbeat received within timeout period"""
        if (datetime.now() - self.last_heartbeat).total_seconds() > self.heartbeat_timeout:
            logger.warning("Heartbeat timeout - closing connection")
            # Custom code for heartbeat timeout
            await self.close(code=CLOSE_CODE_HEARTBEAT_TIMEOUT)

    async def handle_handshake(self, data: Dict[str, Any]):
        """Process initial client handshake."""
        logger.info(f"Handshake received: {data}")
        await self.send_json({
            "type": MessageTypes.HANDSHAKE.value,
            "status": "confirmed",
            "user_id": str(self.user.id),
            "timestamp": datetime.now().isoformat(),
            "connection_id": self.channel_name
        })

    @database_sync_to_async
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation from database."""
        try:
            return Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error fetching conversation: {str(e)}")
            return None

    @database_sync_to_async
    def save_message_to_db(self, conversation: Conversation, message: str, sender: str,
                           media_id: Optional[str] = None, media_url: Optional[str] = None, media_type: Optional[str] = None):
        """Save message to database with additional media info."""
        try:

            conversation_service.save_message(
                conversation=conversation,
                message=message,
                sender=sender,
                # media_id=media_id,
                # media_url=media_url,
                # media_type=media_type
            )
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            raise

    @database_sync_to_async
    def get_conversation_platform_and_id(self, conversation: Conversation) -> tuple[str, str]:
        """Get platform and social ID from conversation."""
        try:
            socialuser = conversation.socialuser  # safe inside sync context
            return socialuser.platform, socialuser.social_media_id
        except Exception as e:
            logger.error(f"Error getting platform info: {str(e)}")
            raise

    @database_sync_to_async
    def send_facebook_message(self, social_media_id: str, message: str):
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
    def send_whatsapp_message(self, phone_number: str, message: str):
        """Send message via WhatsApp API."""
        try:
            whatsapp_service.WhatsAppService().send_text_message(
                phone_number=phone_number,
                message=message,
            )
        except Exception as e:
            logger.error(f"WhatsApp API error: {str(e)}")
            raise

