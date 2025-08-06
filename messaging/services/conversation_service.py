from ..models import Conversation, ChatMessage

def get_or_create_conversation(user, socialuser):
    conversation, created = Conversation.objects.get_or_create(
        user=user,
        socialuser=socialuser,
        defaults={
            'auto_reply': True  # Default to auto-reply enabled
        }
    )
    return conversation

from typing import Optional, List, Dict, Any

def save_message(conversation, message, sender='business',
                 media_id: Optional[str] = None, media_url: Optional[str] = None,
                 media_type: Optional[str] = None, contacts: Optional[List[Dict[str, Any]]] = None):
    return ChatMessage.objects.create(
        conversation=conversation,
        message=message,
        sender=sender,
        media_id=media_id,
        messenger_media_url=media_url, # Assuming messenger_media_url is used for media_url
        media_type=media_type,
        contacts=contacts
    )