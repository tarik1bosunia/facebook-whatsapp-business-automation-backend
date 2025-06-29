# messaging/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import AnonymousUser
from django.core.serializers.json import DjangoJSONEncoder
from .models import ChatMessage, Conversation, Notification

class UnifiedConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.user_id = str(self.user.id) if self.user.is_authenticated else None
        
        if not self.user_id or self.user == AnonymousUser():
            await self.close(code=4001)
            return

        # Single group for all user communications
        self.user_group = f"user_{self.user_id}"
        
        # Add to user group
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )
        
        # Add to all conversation groups
        await self.join_conversation_groups()
        
        await self.accept()

    async def disconnect(self, close_code):
        # Remove from all groups
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )
        if hasattr(self, 'conversation_groups'):
            for conversation_id in self.conversation_groups:
                group_name = f"conversation_{conversation_id}"
                await self.channel_layer.group_discard(
                    group_name,
                    self.channel_name
                )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'send_message':
            await self.handle_send_message(data)
        elif action == 'mark_read':
            await self.handle_mark_read(data)
        elif action == 'typing':
            await self.handle_typing(data)
        elif action == 'join_conversations':
            await self.join_conversation_groups()

    async def handle_send_message(self, data):
        conversation_id = data.get('conversation_id')
        message = data.get('message')
        # sender_type = data.get('sender_type', SENDER_CHOICES.BUSINESS)
        sender_type = data.get('sender_type', 'business')
        
        if not conversation_id or not message:
            return

        # Create message and broadcast
        message_obj = await self.create_chat_message(
            conversation_id, 
            message, 
            sender_type
        )
        
        # Broadcast to conversation participants
        await self.broadcast_message(message_obj)
        
        # Create and send notifications
        await self.create_and_send_notifications(message_obj)

    async def handle_mark_read(self, data):
        message_id = data.get('message_id')
        if message_id:
            await self.mark_message_as_read(message_id)

    async def handle_typing(self, data):
        conversation_id = data.get('conversation_id')
        is_typing = data.get('is_typing', False)
        
        if conversation_id:
            await self.broadcast_typing_status(conversation_id, is_typing)

    async def chat_message(self, event):
        """Handle new chat messages"""
        await self.send(text_data=json.dumps(event, cls=DjangoJSONEncoder))

    async def notification(self, event):
        """Handle notifications"""
        await self.send(text_data=json.dumps(event, cls=DjangoJSONEncoder))

    async def message_status(self, event):
        """Handle message read status updates"""
        await self.send(text_data=json.dumps(event))

    async def typing_indicator(self, event):
        """Handle typing indicators"""
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def join_conversation_groups(self):
        """Join all conversation groups for the user"""
        conversations = Conversation.objects.filter(participants=self.user).values_list('id', flat=True)
        self.conversation_groups = [str(conv_id) for conv_id in conversations]
        
        channel_layer = get_channel_layer()
        for conv_id in self.conversation_groups:
            group_name = f"conversation_{conv_id}"
            async_to_sync(channel_layer.group_add)(
                group_name,
                self.channel_name
            )

    @database_sync_to_async
    def create_chat_message(self, conversation_id, content, sender_type):
        conversation = Conversation.objects.get(id=conversation_id)
        return ChatMessage.objects.create(
            conversation=conversation,
            sender=sender_type,
            message=content
        )

    async def broadcast_message(self, message_obj):
        """Broadcast message to conversation participants"""
        conversation_id = str(message_obj.conversation.id)
        group_name = f"conversation_{conversation_id}"
        
        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'chat_message',
                'action': 'new_message',
                'message_id': str(message_obj.id),
                'conversation_id': conversation_id,
                'sender_type': message_obj.sender,
                'message': message_obj.message,
                'timestamp': message_obj.created_at.isoformat(),
                'media_url': message_obj.messenger_media_url or None,
            }
        )

    async def broadcast_typing_status(self, conversation_id, is_typing):
        """Broadcast typing status to conversation participants"""
        group_name = f"conversation_{conversation_id}"
        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'typing_indicator',
                'action': 'typing',
                'conversation_id': conversation_id,
                'user_id': self.user_id,
                'is_typing': is_typing,
            }
        )

    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        """Mark message as read and update notifications"""
        message = ChatMessage.objects.select_related('conversation').get(id=message_id)
        message.is_read = True
        message.save(update_fields=['is_read'])
        
        # Update notifications
        Notification.objects.filter(
            message=message,
            user=self.user,
            is_read=False
        ).update(is_read=True)
        
        return message.conversation.id

    async def create_and_send_notifications(self, message_obj):
        """Create notifications and send to recipients"""
        conversation = message_obj.conversation
        participants = await self.get_conversation_participants(conversation.id)
        
        for user in participants:
            if user.id == self.user.id:
                continue  # Skip sender
                
            notification = await self.create_notification(user, message_obj, conversation)
            
            # Send notification to recipient's personal group
            await self.channel_layer.group_send(
                f"user_{user.id}",
                {
                    'type': 'notification',
                    'action': 'new_notification',
                    'notification_id': str(notification.id),
                    'conversation_id': str(conversation.id),
                    'message_id': str(message_obj.id),
                    'notification_type': 'message',
                    'timestamp': notification.created_at.isoformat(),
                    'is_read': False,
                }
            )

    @database_sync_to_async
    def get_conversation_participants(self, conversation_id):
        conversation = Conversation.objects.get(id=conversation_id)
        return list(conversation.participants.all())

    @database_sync_to_async
    def create_notification(self, user, message_obj, conversation):
        return Notification.objects.create(
            user=user,
            message=message_obj,
            conversation=conversation,
            notification_type='message'
        )