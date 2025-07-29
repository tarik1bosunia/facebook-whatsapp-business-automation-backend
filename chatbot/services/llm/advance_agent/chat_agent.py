import json
import logging
import uuid
from typing import Any, Dict

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import sync_to_async

from langchain.agents import AgentExecutor, AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

from chatbot.services.llm.llm_factory import LLMFactory
from chatbot.services.llm.tool_manager import ToolManager
from chatbot.services.llm.vector_store import VectorStoreManager
from messaging.models.chatmessage import ChatMessage
from messaging.enums import SENDER_CHOICES
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough

logger = logging.getLogger(__name__)

# I want to make a tool like:: 

class ChatAgent:
    def __init__(self, user, conversation=None):
        self.user = user
        self.conversation = conversation
        self.history = None
        self.memory = None
        self._validate_initialization()
        logger.info("Initializing ChatAgent")

        try:
            self.config = self._get_ai_config()
            self.llm = LLMFactory.create_llm(
                model_code=self.config.ai_model.code,
                api_key=self.config.api_key
            )
            self.vector_store = VectorStoreManager.create_vector_store(
                connection_string=settings.DATABASE_URL,
                collection_name=f"user_{self.user.id}_docs",
                embedding_dim=1536
            )
            self.tool_manager = ToolManager(self.user, self.vector_store)
        except Exception as e:
            logger.critical(f"Agent initialization failed: {str(e)}")
            raise RuntimeError("Agent initialization failed") from e

    async def initialize(self):
        """Initialize agent asynchronously"""
        await self._initialize_history()
        self.agent = await self._create_agent()

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

        message_objects = []
        for msg in messages:
            try:
                content = msg.message[:4000] # Truncate long messages
                if msg.sender == SENDER_CHOICES.CUSTOMER:
                    message_objects.append(HumanMessage(content=content))
                else:
                     message_objects.append(AIMessage(content=content))
            except Exception as e:
                logger.warning(f"Failed to load message {msg.id}: {str(e)}")

        if message_objects:
            try:
                await self.history.aadd_messages(message_objects)
            except Exception as e:
                logger.error(f"Failed to load messages into Redis: {str(e)}")
                raise
        logger.info("Finished loading messages into Redis memory")

    def _validate_initialization(self):
        """Validate required attributes exist"""
        if not hasattr(self.user, 'ai_config'):
            raise ValueError("User model must have ai_config relation")
        if self.conversation and not hasattr(self.conversation, 'id'):
            raise ValueError("Conversation must have id field")

    def _get_ai_config(self):
        try:
            config = self.user.ai_config
            if not config.ai_model:
                raise ValueError("AI model not configured")
            return config
        except ObjectDoesNotExist:
            logger.error(f"No AI config for user {self.user.id}")
            raise ValueError("User has no AI configuration")
        except Exception as e:
            logger.error(f"Config error: {str(e)}")
            raise

    async def _create_agent(self) -> AgentExecutor:
        """Create and configure the agent with tools and memory"""
        tools = self.tool_manager.get_tools()
          # Convert tools to a dictionary for better access
        tool_map = {tool.name: tool for tool in tools}
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = (
            RunnablePassthrough.assign(
                agent_scratchpad=lambda x: self._format_to_messages(x["intermediate_steps"])
            )
            | prompt
            | self.llm
        )

        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            return_intermediate_steps=True,

        )

        # prompt_text = self._get_agent_prompt()
        # prompt_template = PromptTemplate(
        #     input_variables=['input', 'chat_history'],
        #     template=prompt_text
        # )

        # # To debug prompt with sample inputs (replace with your test input and memory content)
        # test_prompt = prompt_template.format(
        #     input="What was my previous question?",
        #     chat_history=self.memory.load_memory_variables({}).get('chat_history', '')
        # )
        # logger.info(f"Final agent prompt:\n{test_prompt}")

        # return initialize_agent(
        #     tools=self.tool_manager.get_tools(),
        #     llm=self.llm,
        #     agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        #     verbose=True,
        #     max_iterations=3,
        #     handle_parsing_errors=True,
        #     memory=self.memory,
        #     agent_kwargs={
        #         'prefix': self._get_agent_prompt(),
        #         'input_variables': ['input', 'chat_history']
        #     }
        # )

    def _get_system_prompt(self) -> str:
        """Generate the system prompt with brand persona"""
        return (
            f"You are {self.config.brand_persona}, representing {self.user.get_full_name()}, the business owner.\n"
            f"You are chatting with a customer on behalf of {self.user.get_full_name()}.\n"
            f"Respond in a {self.config.response_tone.lower()} tone.\n"
            "When unsure, say 'I don't know' rather than guessing.\n"
            "Always use tools to look up information when needed."
        )

    def _get_agent_prompt(self) -> str:
        return (
            f"You are {self.config.brand_persona}, representing {self.user.get_full_name()}, the business owner.\n"
            f"You are chatting with a customer on behalf of {self.user.get_full_name()}.\n"
            f"Here is the conversation so far:\n{{chat_history}}\n"
            f"Respond in a {self.config.response_tone.lower()} tone .\n"
            "When unsure, say 'I don't know' rather than guessing."
        )
    
    def _format_to_messages(self, intermediate_steps):
        """
        Convert intermediate steps to scratchpad messages.
        Handles both AgentAction objects and tuple-based actions.
        """
        from langchain_core.messages import AIMessage, FunctionMessage

        messages = []
        for step in intermediate_steps:
            # Unpack tuple
            if isinstance(step, tuple) and len(step) == 2:
                action, observation = step
            else:
                # Unexpected format, skip
                continue

            # Extract tool name
            tool_name = None
            log_content = None

            # Case 1: Proper AgentAction
            if hasattr(action, "tool"):
                tool_name = action.tool
                log_content = getattr(action, "log", str(action))

            # Case 2: Tuple or dict fallback
            elif isinstance(action, tuple) and len(action) == 2:
                tool_name, log_content = action
            elif isinstance(action, dict):
                tool_name = action.get("tool") or "unknown_tool"
                log_content = action.get("log", str(action))
            else:
                tool_name = "unknown_tool"
                log_content = str(action)

            # Append AI message (thought)
            messages.append(AIMessage(content=log_content))

            # Append function message (tool response)
            if observation is not None:
                messages.append(FunctionMessage(
                    name=tool_name,
                    content=str(observation)
                ))

        return messages

    
    async def get_response(self, message: str) -> Dict[str, Any]:
        if not hasattr(self, 'agent'):
            await self.initialize()

        # await self.history.aclear()    

        # debug print memory contents
        memory_vars = self.memory.load_memory_variables({})
        logger.info(f"Memory variables before agent call: {memory_vars}") 
        logger.info(f"Available tools: {[t.name for t in self.tool_manager.get_tools()]}")   

        try:
            clean_msg = message.strip()[:4000]
            if not clean_msg:
                raise ValueError("Empty message")

            logger.debug(f"Sending message to agent: {clean_msg}")
            result = await self.agent.ainvoke({"input": clean_msg})

            if self.history:
                await self.history.aadd_messages([
                    HumanMessage(content=clean_msg),
                    AIMessage(content=result["output"])
                ])
            return {
                'status': 'success',
                'response': result["output"],
                'model': self.config.ai_model.code,
                'intermediate_steps': result.get("intermediate_steps", [])
            }
        
        except Exception as e:
            logger.error(f"Full error traceback:", exc_info=True)  # Critical for debugging
            return {
                'status': 'error',
                'error': str(e),  # Return actual error message
                'fallback': "Please try again later",
                'debug_info': {
                    'llm_configured': bool(self.llm),
                    'tools_loaded': bool(self.tool_manager.get_tools()),
                    'memory_ready': bool(self.memory)
                }
            }
