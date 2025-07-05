# messaging/services/chat_message_service.py

from concurrent.futures import ThreadPoolExecutor
import os
import time
import re
import requests
import tempfile
from io import BytesIO
from urllib.parse import urlparse
from django.core.files import File
from django.db import transaction, DatabaseError
from typing import TypedDict, List, Optional
from messaging.models import ChatMessage, Conversation
from messaging.services import websocket_service
from threading import Lock
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Contact(TypedDict):
    name: str
    phones: List[str]

class ChatMessageService:
    """
    Service for creating and managing ChatMessage objects with robust media handling.
    Features:
    - Retry logic for failed downloads
    - Sophisticated media type detection
    - Large file handling with streaming
    - Thread-safe async downloads
    - Comprehensive error handling
    """

    # Configuration constants
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    SMALL_FILE_THRESHOLD = 5 * 1024 * 1024  # 5MB
    LARGE_FILE_THRESHOLD = 20 * 1024 * 1024  # 20MB
    MAX_ALLOWED_SIZE = 25 * 1024 * 1024  # 25MB
    DOWNLOAD_TIMEOUT = 30  # seconds
    STALE_DOWNLOAD_THRESHOLD = timedelta(hours=1)  # Consider downloads stale after 1 hour

    _executor = None
    _executor_lock = Lock()

    @classmethod
    @transaction.atomic
    def create_message(
        cls,
        conversation: Conversation,
        sender: str,
        *,
        message: Optional[str] = None,
        media_id: Optional[str] = None,
        media_type: Optional[str] = None,
        contacts: Optional[List[Contact]] = None,
        messenger_media_url: Optional[str] = None,
        messenger_media_file=None,
    ) -> ChatMessage:
        """Create a new ChatMessage with validation and async media download."""
        cls._validate_input(
            sender=sender,
            message=message,
            media_id=media_id,
            media_type=media_type,
            contacts=contacts,
            messenger_media_url=messenger_media_url,
            messenger_media_file=messenger_media_file,
        )

        if messenger_media_url and not messenger_media_file:
            cls._start_async_download(
                messenger_media_url,
                conversation.id,
                sender,
                message,
                media_id,
                media_type,
                contacts
            )
            return cls._create_message_without_file(
                conversation,
                sender,
                message,
                media_id,
                media_type,
                contacts,
                messenger_media_url
            )

        return cls._create_message_with_file(
            conversation,
            sender,
            message,
            media_id,
            media_type,
            contacts,
            messenger_media_url,
            messenger_media_file
        )

    @classmethod
    def _create_message_with_file(
        cls,
        conversation: Conversation,
        sender: str,
        message: Optional[str],
        media_id: Optional[str],
        media_type: Optional[str],
        contacts: Optional[List[Contact]],
        messenger_media_url: Optional[str],
        messenger_media_file: Optional[File]
    ) -> ChatMessage:
        """Create message with existing file."""
        chat_message = ChatMessage.objects.create(
            conversation=conversation,
            sender=sender,
            message=message,
            media_id=media_id,
            media_type=media_type,
            contacts=contacts,
            messenger_media_url=messenger_media_url,
            messenger_media_file=messenger_media_file,
            download_status='completed'
        )
        
        cls._send_websocket_notification(
            conversation,
            sender,
            message,
            media_id,
            media_type,
            contacts,
            messenger_media_url
        )
        return chat_message

    @classmethod
    def _create_message_without_file(
        cls,
        conversation: Conversation,
        sender: str,
        message: Optional[str],
        media_id: Optional[str],
        media_type: Optional[str],
        contacts: Optional[List[Contact]],
        messenger_media_url: str
    ) -> ChatMessage:
        """Create message placeholder for async download."""
        chat_message = ChatMessage.objects.create(
            conversation=conversation,
            sender=sender,
            message=message,
            media_id=media_id,
            media_type=media_type,
            contacts=contacts,
            messenger_media_url=messenger_media_url,
            download_status='pending'
        )
        
        cls._send_websocket_notification(
            conversation.id,
            sender,
            message,
            media_id,
            media_type,
            contacts,
            messenger_media_url
        )
        return chat_message

    @classmethod
    def _send_websocket_notification(
        cls,
        conversation: Conversation,
        sender: str,
        message: Optional[str],
        media_id: Optional[str],
        media_type: Optional[str],
        contacts: Optional[List[Contact]],
        media_url: Optional[str],
    ):
        """Send consistent websocket notifications."""
        websocket_service.message_from_outside_consumer(
            conversation=conversation,
            sender=sender,
            message_text=message,
            media_id=media_id,
            media_type=media_type,
            contacts=contacts,
            media_url=media_url,
        )

    @classmethod
    def _start_async_download(
        cls,
        url: str,
        conversation_id: int,
        sender: str,
        message: Optional[str],
        media_id: Optional[str],
        media_type: Optional[str],
        contacts: Optional[List[Contact]]
    ):
        """Start thread-safe async download."""
        with cls._executor_lock:
            if cls._executor is None:
                cls._executor = ThreadPoolExecutor(max_workers=4)
        
        cls._executor.submit(
            cls._download_and_update_message,
            url,
            conversation_id,
            sender,
            message,
            media_id,
            media_type,
            contacts
        )

    @classmethod
    def _download_and_update_message(
        cls,
        url: str,
        conversation_id: int,
        sender: str,
        message: Optional[str],
        media_id: Optional[str],
        media_type: Optional[str],
        contacts: Optional[List[Contact]]
    ):
        """Download file and update message with comprehensive error handling."""
        try:
            # 1. Get message with stale download check
            chat_message = cls._get_chat_message_for_download(
                conversation_id,
                sender,
                message,
                url
            )
            if not chat_message:
                return

            # 2. Download file
            file_obj = cls._download_with_retry(url)
            
            # 3. Determine media type
            detected_type = cls._determine_media_type(file_obj, url)
            final_media_type = media_type or detected_type
            
            # 4. Save to message
            with transaction.atomic():
                chat_message.refresh_from_db()
                if chat_message.messenger_media_file:
                    logger.info(f"Message {chat_message.id} already has file")
                    return
                
                filename = cls._get_filename(url, final_media_type)
                chat_message.messenger_media_file.save(filename, file_obj)
                chat_message.media_type = final_media_type
                chat_message.download_status = 'completed'
                chat_message.save()

            # 5. Notify clients
            websocket_service.media_ready_notification(
                group_name=f'conversation_{conversation_id}',
                message_id=chat_message.id
            )

        except Exception as e:
            logger.error(f"Failed to process {url}: {str(e)}", exc_info=True)
            cls._mark_download_failed(conversation_id, sender, message, url)

    @classmethod
    def _get_chat_message_for_download(
        cls,
        conversation_id: int,
        sender: str,
        message: Optional[str],
        url: str
    ) -> Optional[ChatMessage]:
        """Retrieve message for download with error handling."""
        try:
            chat_message = ChatMessage.objects.get(
                conversation_id=conversation_id,
                sender=sender,
                message=message,
                messenger_media_url=url,
                messenger_media_file=None
            )
            
            # Check for stale downloads
            if (datetime.now(chat_message.created_at.tzinfo) - chat_message.created_at > 
                cls.STALE_DOWNLOAD_THRESHOLD):
                logger.warning(f"Skipping stale download for message {chat_message.id}")
                chat_message.download_status = 'failed'
                chat_message.save()
                return None
                
            return chat_message
            
        except ChatMessage.DoesNotExist:
            logger.error(f"No ChatMessage found for {url}")
            return None
        except ChatMessage.MultipleObjectsReturned:
            logger.error(f"Multiple messages found for {url}, using latest")
            return ChatMessage.objects.filter(
                conversation_id=conversation_id,
                messenger_media_url=url,
                messenger_media_file=None
            ).latest('created_at')

    @classmethod
    def _mark_download_failed(
        cls,
        conversation_id: int,
        sender: str,
        message: Optional[str],
        url: str
    ):
        """Update message status when download fails."""
        try:
            with transaction.atomic():
                chat_message = ChatMessage.objects.get(
                    conversation_id=conversation_id,
                    sender=sender,
                    message=message,
                    messenger_media_url=url,
                    messenger_media_file=None
                )
                chat_message.download_status = 'failed'
                chat_message.save()
        except Exception as e:
            logger.error(f"Failed to mark download failed: {str(e)}")

    @classmethod
    def _download_with_retry(cls, url: str) -> File:
        """Download file with retry logic."""
        for attempt in range(1, cls.MAX_RETRIES + 1):
            try:
                return cls._download_file(url)
            except Exception as e:
                if attempt == cls.MAX_RETRIES:
                    raise
                logger.warning(f"Attempt {attempt} failed for {url}: {str(e)}")
                time.sleep(cls.RETRY_DELAY * attempt)


    @classmethod
    def _download_file(cls, url: str) -> File:
        """Download file with proper handling for large files"""
        # Get content length to determine file size
        head_response = requests.head(url, allow_redirects=True, timeout=5)
        content_length = int(head_response.headers.get('Content-Length', 0))

        if content_length > cls.MAX_ALLOWED_SIZE:  
            raise ValueError("File too large")
        
        # Determine download strategy based on size
        if content_length < cls.SMALL_FILE_THRESHOLD:
            return cls._download_small_file(url)
        else:
            return cls._download_large_file(url, content_length)


    @classmethod
    def _download_small_file(cls, url: str) -> File:
        """Download small files to memory."""
        response = requests.get(url, timeout=(3.05, 10))
        response.raise_for_status()
        return File(BytesIO(response.content))

    @classmethod
    def _download_large_file(cls, url: str, content_length: int) -> File:
        """Stream large files to disk safely."""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            with requests.get(url, stream=True, timeout=cls.DOWNLOAD_TIMEOUT) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
            temp_file.flush()
            return File(open(temp_file.name, 'rb'))
        except Exception:
            os.unlink(temp_file.name)
            raise
        finally:
            temp_file.close()


    @staticmethod
    def _validate_content_type(content_type: str, media_type: str) -> bool:
        """
        Verify that the content type matches the expected media type.
        """
        if media_type == 'image':
            return content_type.startswith('image/')
        elif media_type == 'video':
            return content_type.startswith('video/')
        elif media_type == 'audio':
            # Accept video/mp4 as audio (common with Facebook Messenger)
            return content_type.startswith('audio/') or content_type == 'video/mp4'

        elif media_type == 'file':
        # Accept common document types
            return any(content_type.startswith(prefix) for prefix in [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument',
                'text/plain'
            ])    
        return True  # For other types, don't validate    


    @staticmethod
    def _determine_media_type_from_url(url: str) -> str:
        """
        Determine media type from URL file extension.
        """
        path = urlparse(url).path
        ext = os.path.splitext(path)[1].lower()
        
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return 'image'
        elif ext in ['.mp4', '.mov', '.avi', '.webm']:
            return 'video'
        elif ext in ['.mp3', '.wav', '.ogg']:
            return 'audio'
        else:
            return 'document'

    @classmethod
    def _get_filename(cls, url: str, media_type: str) -> str:
        """Generate appropriate filename"""
        # Extract from URL
        path = urlparse(url).path
        filename = os.path.basename(path)
        
        # Clean filename
        if filename:
            filename = re.sub(r'[^\w\.\-]', '_', filename)
            filename = filename[:100]  # Limit length
        else:
            # Generate filename
            ext_map = {
                'image': '.jpg',
                'video': '.mp4',
                'audio': '.mp3',
                'document': '.bin'
            }
            filename = f"{media_type}_{int(time.time())}{ext_map.get(media_type, '')}"
        
        return filename  


    @staticmethod
    def _validate_input(
        sender: str,
        message: Optional[str],
        media_id: Optional[str],
        media_type: Optional[str],
        contacts: Optional[List[Contact]],
        messenger_media_url: Optional[str],
        messenger_media_file: Optional[str]
    ) -> None:
        """Validate message input combinations."""
        valid_senders = ['customer', 'business', 'ai']
        if sender not in valid_senders:
            raise ValueError(f"Invalid sender type. Must be one of {valid_senders}")

        has_text = bool(message)
        has_media = bool(media_id)
        has_contacts = bool(contacts)
        has_messenger_media = bool(messenger_media_url or messenger_media_file)

        if has_media and (not media_id or not media_type):
            raise ValueError("Both media_id and media_type are required for media messages")

        if has_contacts:
            if not isinstance(contacts, list):
                raise ValueError("Contacts must be a list of dictionaries")
            for contact in contacts:
                if not isinstance(contact, dict):
                    raise ValueError("Each contact must be a dictionary")
                if 'name' not in contact or not isinstance(contact['name'], str):
                    raise ValueError("Each contact must have a 'name' of type string")
                if 'phones' not in contact or not isinstance(contact['phones'], list) or not all(isinstance(p, str) for p in contact['phones']):
                    raise ValueError("Each contact must have a 'phones' list of strings")

        if not (has_text or has_media or has_contacts or has_messenger_media):
            raise ValueError("A message must contain at least one of: text, media, contacts, or Messenger media")

        if messenger_media_url and not messenger_media_file:
            # Media type must be provided or determinable from URL
            if not media_type and not ChatMessageService._determine_media_type_from_url(messenger_media_url):
                raise ValueError("Messenger media must have a media_type or a recognizable file extension")            
                    








    




# messaging/services/chat_message_service.py

# from django.db import transaction
# from messaging.models import ChatMessage, Conversation
# from typing import TypedDict, List, Optional

# from messaging.services import websocket_service


# class Contact(TypedDict):
#     name: str
#     phones: List[str]


# class ChatMessageService:
#     """
#     Service for creating and managing ChatMessage objects.
#     Handles different message types (text, media, contacts) with validation.
#     """

#     @classmethod
#     def create_message(
#         cls,
#         conversation: Conversation,
#         sender: str,
#         *,
#         message: Optional[str] = None,
#         media_id: Optional[str] = None,
#         media_type: Optional[str] = None,
#         contacts: Optional[List[Contact]] = None,
#         messenger_media_url: Optional[str] = None,
#         messenger_media_file=None,
        
#     ) -> ChatMessage:
#         """
#         Create a new ChatMessage with validation for message types.

#         Args:
#             conversation: Conversation instance
#             sender: 'customer', 'business', or 'ai'
#             message: Text content (for text messages or media captions)
#             media_id: Media ID from WhatsApp
#             media_type: Type of media (image, audio, video, etc.)
#             contacts: Contact information (for contact messages)
#             messenger_media_url: url of the messenger attachments
#             messenger_media_file: media file downloaded

#         Returns:
#             Created ChatMessage instance
#         """
#         cls._validate_input(
#             sender=sender,
#             message=message,
#             media_id=media_id,
#             media_type=media_type,
#             contacts=contacts,
#             messenger_media_url=messenger_media_url,
#             messenger_media_file=messenger_media_file,
#         )

#         # sent frontend every message by webhook during creation
#         websocket_service.message_from_outside_consumer(
#             group_name=f'conversation_{conversation.id}', 
#             sender=sender,  
#             message=message, 
#             media_id=media_id, 
#             media_type=media_type, 
#             contacts=contacts,
#             # messenger_media_url=messenger_media_url,
#         )


#         return ChatMessage.objects.create(
#             conversation=conversation,
#             sender=sender,
#             message=message,
#             media_id=media_id,
#             media_type=media_type,
#             contacts=contacts,
#             messenger_media_url=messenger_media_url,
#             messenger_media_file=messenger_media_file
#         )



#         has_messenger_media = bool(messenger_media_url or messenger_media_file)

#         if not (has_text or has_media or has_contacts or has_messenger_media):
#             raise ValueError("A message must contain at least one of: text, media, contacts, or Messenger media")

#         if messenger_media_url and not media_type:
#             raise ValueError("Messenger media must have a media_type")

