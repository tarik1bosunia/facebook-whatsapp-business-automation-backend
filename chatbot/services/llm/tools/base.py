"""
Foundation for all tools
"""

from typing import Type, Any
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain_core.tools import tool

class BaseToolSchema(BaseModel):
    """Base schema for tool inputs"""
    user_id: str = Field(..., description="The authenticated user ID")

class ToolFactory:
    @staticmethod
    def create(tool_class: Type[BaseTool], **kwargs) -> BaseTool:
        """Factory method for creating tools"""
        return tool_class(**kwargs)