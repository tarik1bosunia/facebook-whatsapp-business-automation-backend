from langchain_core.messages import HumanMessage, AIMessage
from .tools import ToolManager
from .llm_factory import LLMFactory
from .prompt import get_formatted_system_prompt
from .config import ConfigManager
from .agent_builder import AgentBuilder

import uuid
from asgiref.sync import sync_to_async
from messaging.models import ChatMessage
from messaging.enums import SENDER_CHOICES

from django.conf import settings

from langchain_community.chat_message_histories import RedisChatMessageHistory

from langchain.memory import ConversationBufferMemory

import logging
logger = logging.getLogger(__name__)

class ChatAgent:
    def __init__(self, user, conversation=None):
        self.user = user
        self.conversation = conversation
        self.system_prompt = get_formatted_system_prompt(self.user)
        self._initialize_componets()


    async def initialize(self):
        """Initialize agent asynchronously"""
        await self._initialize_history()
        # self.agent = await self._create_agent()    


    def _initialize_componets(self):  
        """Initialize all required components"""
        # configuration
        config_manager = ConfigManager(self.user)
        config_manager.validate_initialization(self.conversation)
        self.config = config_manager.get_ai_config()  

        # tools
        self.tools = ToolManager().get_tools()

        # LLM
        self.llm = LLMFactory.create_llm(
            model_code=self.config.ai_model.code,
            api_key=self.config.api_key,
            tools=self.tools,
        )

        # Agent
        self.agent = AgentBuilder.build_agent(
            llm=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt,
            user=self.user
        )

    async def _initialize_history(self):
        """Initialize conversation history from Redis or DB"""
        if not self.conversation:
            return

        self.history = await self._get_async_history()
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
            ttl=60 * 60 * 24 * 7
        ) # 1 week TTL    


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
                    await self.history.aadd_user_message(content)
                else:
                    await self.history.aadd_ai_message(content)
            except Exception as e:
                logger.warning(f"Failed to load message {msg.id}: {str(e)}")

        logger.info("Finished loading messages into Redis memory")    


    async def get_response(self, message: str) -> str:


        await self._initialize_history()
        
        try:
            clean_msg = message.strip()[:4000]
            if not clean_msg:
                raise ValueError("Empty message")
            config = {"configurable": {"thread_id": str(self.conversation.id)}}



            
            if self.history:
                # Get all past messages from Redis
                past_messages = await self.history.aget_messages() if self.history else []
                logger.debug(f"Previous messages in history ({len(past_messages)}):\n" +
                        "\n".join([f"{msg.type}: {msg.content[:100]}..." 
                                 for msg in past_messages]))
            else:
                logger.debug("No conversation history available")
                past_messages = [] 

            # Add the new user message to the message list
            messages = past_messages + [HumanMessage(content=clean_msg)]
    

            result = await self.agent.ainvoke({'messages': messages}, config)

            if self.history and 'messages' in result and len(result['messages']) > 0:
                try:
                    await self.history.aadd_messages([
                        HumanMessage(content=clean_msg),
                        AIMessage(content=result['messages'][-1].content)
                    ])
                    logger.debug("Successfully stored messages in history")
                    
                except Exception as history_error:
                    logger.error(f"Failed to store messages in history: {str(history_error)}")
        
            if result.get('messages'):
                response = result['messages'][-1].content
                logger.info(f"Returning response: {response[:200]}...")
                return response
            logger.warning("Agent returned empty response")
            return "I didn't get that. Could you please rephrase your question?"
        except Exception as e:
            logger.error(f"Error in get_response: {str(e)}")
            return "An error occurred while processing your request. "
        
     

    
