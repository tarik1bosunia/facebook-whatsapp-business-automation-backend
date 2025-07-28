from typing import List, Union, Annotated, TypedDict
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[List[Union[HumanMessage, AIMessage]], add_messages]