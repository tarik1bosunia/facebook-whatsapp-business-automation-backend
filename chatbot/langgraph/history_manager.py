from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage
import uuid
import logging
from asgiref.sync import sync_to_async
from django.conf import settings
from messaging.models import ChatMessage
from messaging.enums import SENDER_CHOICES

logger = logging.getLogger(__name__)

class MessageHistoryManager:
    def __init__(self, user, conversation=None):
        self.user = user
        self.conversation = conversation
        self.history = None
        self.memory = None

    async def initialize(self):
        """Initialize conversation history from Redis or DB"""
        if not self.conversation:
            return

        self.history = await self._get_async_history()
        # await self.history.aclear()     ## clear history if needed

        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            chat_memory=self.history
        )

        existing = await self.history.aget_messages()
        logger.debug(f"Found {len(existing)} existing messages in Redis")

        if not existing:
            await self._load_history_messages()    

    async def _get_async_history(self):
        session_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"conversation-{self.conversation.id}"))
        return RedisChatMessageHistory(
            session_id=session_id,
            url=settings.REDIS_URL,
            # ttl=60 * 60 * 24 * 7 # 1 week TTL TODO: adjust for production
            ttl=60 # 1 minute TTL for testing
        )     

    async def _load_history_messages(self):
        """Load conversation history from database into Redis"""
        messages = await sync_to_async(
            lambda: list(ChatMessage.objects.filter(conversation=self.conversation)
                         .order_by('created_at')
                         .only('sender', 'message'))
        )()

        logger.info(f"Loading {len(messages)} messages from DB into Redis")

        for msg in messages:
            try:
                content = msg.message[:4000] # Truncate long messages
                if msg.sender == SENDER_CHOICES.CUSTOMER:
                    await self.history.add_message(HumanMessage(content=content))
                else:
                    await self.history.add_message(AIMessage(content=content))
            except Exception as e:
                logger.warning(f"Failed to load message {msg.id}: {str(e)}")

        logger.info("Finished loading messages into Redis memory")

    async def get_past_messages(self):
        """Get all past messages from history"""
        return await self.history.aget_messages() if self.history else []

    async def add_message_pair(self, user_message, ai_message):
        """Add a pair of user and AI messages to history"""
        if not self.history:
            return

        try:
            await self.history.aadd_messages([
                HumanMessage(content=user_message),
                AIMessage(content=ai_message)
            ])
            logger.debug("Successfully stored messages in history")
        except Exception as e:
            logger.error(f"Failed to store messages in history: {str(e)}")