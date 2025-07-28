from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import make_call_llm, make_take_action, make_should_continue

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.redis import RedisSaver
from django.conf import settings

class AgentBuilder:
    
    @classmethod
    def build_agent(cls, llm, tools, system_prompt, user):
        checkepointer = MemorySaver()
        # with RedisSaver.from_conn_string(settings.REDIS_URL) as checkpointer:
            # checkpointer.setup()

        call_llm_node = make_call_llm(system_prompt, llm)
        take_action_node = make_take_action(tools)
        should_continue_node = make_should_continue(user)
            
        graph = StateGraph(AgentState)
        graph.add_node("llm", call_llm_node)
        graph.add_node("retriever_agent", take_action_node)

        graph.add_conditional_edges(
            "llm",
            should_continue_node,
            {True: "retriever_agent", False: END}
        )
        graph.add_edge("retriever_agent", "llm")
        graph.set_entry_point("llm")

        return graph.compile(checkpointer=checkepointer)