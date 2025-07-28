from .state import AgentState
from langchain_core.messages import SystemMessage, ToolMessage


def make_call_llm(system_prompt, llm):
    def call_llm(state: AgentState) -> AgentState:
        """Function to call the LLM with the current state."""
        messages = [SystemMessage(content=system_prompt)] + list(state['messages'])
        message = llm.invoke(messages)
        return {'messages': [message]}
    return call_llm

# Retriever Agent
def make_take_action(tools):
    def take_action(state: AgentState) -> AgentState:
        tool_calls = state['messages'][-1].tool_calls
        tools_dict = {tool.name: tool for tool in tools}
        results = []

        for t in tool_calls:
            tool = tools_dict.get(t['name'])
            result = tool.invoke(t['args']) if tool else "Invalid tool name"
            results.append(ToolMessage(
                tool_call_id=t['id'], name=t['name'], content=str(result)))
        
        return {'messages': results}
    
    return take_action


def make_should_continue(user):
    def should_continue(state: AgentState):
        """Check if the last message contains tool calls."""
        result = state['messages'][-1]
        print(f"Last message: {result}")
        if hasattr(result, 'usage_metadata'):
            usage_metadata = result.usage_metadata
            usage_metadata = {
                "input_tokens": usage_metadata.get('input_tokens', 0),
                "output_tokens": usage_metadata.get('output_tokens', 0),
                "total_tokens": usage_metadata.get('total_tokens', 0)

            }
            user_config = user.ai_config
            user_config.update_token_counts(usage_metadata)

            # print(f"Usage metadata: {usage_metadata}")
            # print(f"token info: {token_info}")

        
        return hasattr(result, 'tool_calls') and len(result.tool_calls) > 0
    
    return should_continue