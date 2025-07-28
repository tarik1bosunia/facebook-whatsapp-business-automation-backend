from langchain_core.messages import HumanMessage
from .tools import ToolManager
from .llm_factory import LLMFactory
from .prompt import get_formatted_system_prompt
from .config import ConfigManager
from .agent_builder import AgentBuilder
import logging

logger = logging.getLogger(__name__)

class AgentCore:
    def __init__(self, user, conversation=None):
        self.user = user
        self.conversation = conversation
        self.system_prompt = get_formatted_system_prompt(self.user)
        self._initialize_components()

    def _initialize_components(self):  
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

    async def generate_response(self, messages, config=None):
        """Generate response from the agent"""
        if config is None:
            config = {"configurable": {"thread_id": str(self.conversation.id)}}
        
        try:
            return await self.agent.ainvoke({'messages': messages}, config)
        except Exception as e:
            logger.error(f"Error in agent response generation: {str(e)}")
            raise