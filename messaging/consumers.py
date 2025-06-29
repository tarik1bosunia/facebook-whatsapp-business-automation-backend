from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json
from datetime import datetime, timedelta
from enum import Enum 

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
    async def connect(self):
        print("===================== WEBSOCKET CONNECTING =======================")
        print('websocket connected...')
        print('scope', self.scope)  
        print('channel layer::', self.channel_layer)
        print('channel name::', self.channel_name)

        self.group_name = 'global_chat'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        self.last_heartbeat = datetime.now()



    # def save_chat_to_database(self, message):
    #     group = Group.objects.filter(name=self.group_name).first()
    #     Chat.objects.create(content=message, group=group)  

    async def receive_json(self, content, **kwargs):
        """Handle incoming WebSocket messages."""
        print("=============== WEBSOCKET MESSAGE RECEIVED ===============")
        print("Received message:", content)

        message_type = content.get("type")

        if message_type == "heartbeat":
            self.last_heartbeat = datetime.now()
            print("Heartbeat received")
            await self.send_heartbeat_response()
            return

        if message_type == "handshake":
            await self.handle_handshake(content)
            return
        
        # Handle regular messages
        await self.handle_message(content)
        await self.check_connection_health()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.close(code=1000)

    async def chat_message(self, event):
        """Broadcast message to all clients except sender."""
        if event.get("sender_channel") == self.channel_name:
            return  # Skip if this is the sender's channel
        
         # Forward the message to the client as text
        # message = json.loads(event['message'])
        # conversation_id = message.pop('conversation_id', None)

        message = json.loads(event["message"])

        await self.send_json({
            "type": "new_message",
            "payload": message
        })

        
        await self.send(text_data=json.dumps({
            "type": "new_message",
            "payload": message
        }))    


    async def send_heartbeat_response(self):
        """Send heartbeat acknowledgment."""
        await self.send_json({
            "type": "heartbeat",
            "status": "ok",
            "timestamp": datetime.now().isoformat()
        })

    async def handle_message(self, content):
        """Process and broadcast chat messages."""
        # Extract data
        conversation_id = content.get('conversation_id')
        message = content.get('message')


        if not conversation_id or not message:
            print("Error: Missing conversation_id or message")
            return
        
 
       
        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat.message',
                'message': json.dumps({
                    'conversation_id': conversation_id,
                    'message': message
                }),
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
        await self.send_json({"type": "handshake", "status": "success"})
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






