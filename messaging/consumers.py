from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json
from datetime import datetime, timedelta
from enum import Enum

from django.contrib.auth.models import AnonymousUser

from messaging.models.conversation import Conversation
from messaging.services import conversation_service, whatsapp_service
from messaging.utils import facebook_api


class MessageTypes(Enum):
    HEARTBEAT = "heartbeat"
    HANDSHAKE = "handshake"
    NEW_MESSAGE = "new_message"
    NOTIFICATION = "notification"


class ChatAsyncJsonWebsocketConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_heartbeat = None
        self.heartbeat_timeout = 40  # seconds
        self.heartbeat_interval = 30  # seconds
        self.user = None
        self.group_name = None

    async def connect(self):
        print("===================== WEBSOCKET CONNECTING =======================")
        print('websocket connected...')
        print('scope', self.scope)
        print('channel layer::', self.channel_layer)
        print('channel name::', self.channel_name)

        # Get authenticated user from scope (set by JWTAuthMiddleware)
        self.user = self.scope["user"]

        if isinstance(self.user, AnonymousUser):
            print("Unauthenticated connection attempt")
            # Custom close code for unauthenticated
            await self.close(code=4001)
            return

        print(f"Authenticated as user: {self.user.id}")

        # self.group_name = 'global_chat'
        self.group_name = f'user_{self.user.id}_chat'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        self.last_heartbeat = datetime.now()

       # Send initial handshake with user info
        await self.send_json({
            "type": MessageTypes.HANDSHAKE.value,
            "status": "authenticated",
            "user_id": str(self.user.id),
            "timestamp": datetime.now().isoformat()
        })

    # def save_chat_to_database(self, message):
    #     group = Group.objects.filter(name=self.group_name).first()
    #     Chat.objects.create(content=message, group=group)

    async def receive_json(self, content, **kwargs):
        """Handle incoming WebSocket messages."""
        if not self.user or isinstance(self.user, AnonymousUser):
            await self.close(code=4001)
            return

        print("Received message:", content)

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
            payload = message_type = content.get("payload")
            if payload:
                await self.handle_message(payload)

        # Handle regular messages
        await self.check_connection_health()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        await self.close(code=close_code)

    async def chat_message(self, event):
        """Handle incoming chat messages from the group."""
        if event.get("sender_channel") == self.channel_name:
            return  # Skip if this is the sender's channel

        # Forward the message to the client as text
        # message = json.loads(event['message'])
        # conversation_id = message.pop('conversation_id', None)

        try:
            message = json.loads(event["message"])
            await self.send_json({
                "type": MessageTypes.NEW_MESSAGE.value,
                "payload": {
                    **message,
                    "received_at": datetime.now().isoformat()
                }
            })

            await self.send(text_data=json.dumps({
                "type": "new_message",
                "payload": message
            }))

        except json.JSONDecodeError as e:
            print(f"Error decoding message: {str(e)}")

    async def send_heartbeat_response(self):
        """Send heartbeat acknowledgment."""
        await self.send_json({
            "type": MessageTypes.HEARTBEAT.value,
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "next_expected_in": self.heartbeat_interval
        })

    @database_sync_to_async
    def get_conversation(self, conversation_id):
        try:
            return Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message_to_db(self, conversation, message, sender):
        conversation_service.save_message(
            conversation=conversation,
            message=message,
            sender=sender,
        )

    @database_sync_to_async
    def get_conversation_platform_and_id(self, conversation):
        socialuser = conversation.socialuser  # safe inside sync context
        return socialuser.platform, socialuser.social_media_id

    async def handle_message(self, payload):
        """Process and broadcast chat messages."""
        # Extract data
        conversation_id = payload.get('conversation_id')
        message_text = payload.get('text')
        media_id = payload.get('media_id')
        media_type = payload.get('media_type')
        media_url = payload.get('media_url')
        contacts = payload.get('contacts', [])

        print("=============== WEBSOCKET MESSAGE RECEIVED ===============")

        print("conversation id::", conversation_id)
        print("message::", message_text)

        if not conversation_id or not message_text:
            print("Error: Missing conversation_id or message")
            return

        # Get conversation from database
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            print(f"Conversation {conversation_id} not found")
            return

        # Save message to database
        await self.save_message_to_db(conversation, message_text, 'business')

        # Fetch platform and social ID safely
        platform, social_media_id = await self.get_conversation_platform_and_id(conversation)

        # Handle platform-specific messaging
        if platform == 'facebook':
            await self.send_facebook_message(social_media_id, message_text)
        elif platform == 'whatsapp':
            await self.send_whatsapp_message(social_media_id, message_text)

        # Add user info to the message
        # TODO : here need to decide which data i will sent
        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat.message',
                'message': json.dumps({
                    # Ensure string type
                    "conversation_id": str(conversation_id),
                    "message": {
                        "id": f"ws-{int(datetime.now().timestamp() * 1000)}",
                        "text": message_text,
                        "time": datetime.now().isoformat(),
                        "sender": "business",  # or determine dynamically
                        "media_id": payload.get('media_id'),
                        "media_url": payload.get('media_url'),
                        "media_type": payload.get('media_type'),
                        "contacts": payload.get('contacts', []),
                        "conversation_id": str(conversation_id),
                    }}),
                'sender_channel': self.channel_name
            }
        )

    async def check_connection_health(self):
        """Close connection if no heartbeat received within timeout period"""
        if (datetime.now() - self.last_heartbeat).total_seconds() > self.heartbeat_timeout:
            await self.close(code=4002)  # Custom code for heartbeat timeout

    async def handle_handshake(self, data):
        """Process initial client handshake."""
        print("Handshake received:", data)
        await self.send_json({
            "type": MessageTypes.HANDSHAKE.value,
            "status": "confirmed",
            "user_id": str(self.user.id),
            "timestamp": datetime.now().isoformat()
        })

    @database_sync_to_async
    def send_facebook_message(self, social_media_id, message):
        facebook_api.send_message(social_media_id, message)

    @database_sync_to_async
    def send_whatsapp_message(self, phone_number, message):
        whatsapp_service.WhatsAppService().send_text_message(
            phone_number=phone_number,
            message=message,
        )
# ====================== BACKUP ================================

# from channels.generic.websocket import AsyncJsonWebsocketConsumer
# from channels.db import database_sync_to_async
# import json

# # from .models import Chat, Group

# class ChatAsyncJsonWebsocketConsumer(AsyncJsonWebsocketConsumer):
#     async def connect(self):
#         print('websocket connected...')
#         print('scope', self.scope)
#         self.conversation_id = self.scope["query_string"].decode().split("conversation_id=")[-1]
#         print('conversation_id', self.conversation_id)
#         print('channel layer::', self.channel_layer)
#         print('channel name::', self.channel_name)
#         self.group_name = f"conversation_{self.conversation_id}"
#         print("Joining group:", self.group_name)

#         await self.channel_layer.group_add(self.group_name, self.channel_name)
#         await self.accept()


#     # def save_chat_to_database(self, message):
#     #     group = Group.objects.filter(name=self.group_name).first()
#     #     Chat.objects.create(content=message, group=group)

#     async def receive_json(self, content, **kwargs):
#         print("message receive from client...", content)
#         message = content['message']

#         # await database_sync_to_async(self.save_chat_to_database)(message=message)

#         await self.channel_layer.group_send(
#             self.group_name,
#             {
#                 'type': 'chat.message',
#                 'message': json.dumps({'message': message})
#             }
#         )


#     async def disconnect(self, close_code):
#         await self.close(code=1000)

#     async def chat_message(self, event):
#         await self.send(text_data=event['message'])
