from .agent_core import AgentCore
from .history_manager import MessageHistoryManager
from langchain_core.messages import HumanMessage
import logging

logger = logging.getLogger(__name__)

class ChatAgent:
    def __init__(self, user, conversation=None):
        self.user = user
        self.conversation = conversation
        self.agent_core = AgentCore(user, conversation)
        self.history_manager = MessageHistoryManager(user, conversation)

    async def initialize(self):
        """Initialize agent asynchronously"""
        await self.history_manager.initialize()

    async def get_response(self, message: str) -> str:
        """Get response from the agent"""
        await self.initialize()
        
        try:
            clean_msg = message.strip()[:4000]
            if not clean_msg:
                raise ValueError("Empty message")

            # Get past messages
            past_messages = await self.history_manager.get_past_messages()
            logger.debug(f"Previous messages in history ({len(past_messages)}):\n" +
                    "\n".join([f"{msg.type}: {msg.content[:100]}..." 
                             for msg in past_messages]))

            # Prepare messages for the agent
            messages = past_messages + [HumanMessage(content=clean_msg)]
    
            # Get agent response
            result = await self.agent_core.generate_response(messages)

            # Handle response and store in history
            if result.get('messages'):
                response = result['messages'][-1].content
                await self.history_manager.add_message_pair(clean_msg, response)
                logger.info(f"Returning response: {response[:200]}...")
                return response
                
            logger.warning("Agent returned empty response")
            return "I didn't get that. Could you please rephrase your question?"
            
        except Exception as e:
            logger.error(f"Error in get_response: {str(e)}")
            return "An error occurred while processing your request."