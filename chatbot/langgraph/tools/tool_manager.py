from langchain_core.tools import tool, BaseTool
from typing import List, Dict, Any, Type
import logging
from pydantic import BaseModel, Field
from .product_search_tool import ProductSearchTool
from .faq_search_tool import FAQSearchTool

logger = logging.getLogger(__name__)


class ToolManager:
    """Manager for all available tools with proper initialization and error handling"""


    @classmethod
    def get_tools(cls) -> List[BaseTool]:
        """Get all available tools with initialization checks"""
        try:
            return [
                AddTool(),
                SubtractTool(),
                MultiplyTool(),
                DivideTool(),
                ProductSearchTool(),
                FAQSearchTool(),
            ]
        except Exception as e:
            logger.error(f"Failed to initialize tools: {str(e)}")
            raise RuntimeError("Tool initialization failed") from e



class BaseMathTool(BaseTool):
    """Base class for math operation tools."""

    # Each math tool will have structured input
    class InputSchema(BaseModel):
        a: float = Field(..., description="First number")
        b: float = Field(..., description="Second number")

    args_schema: Type[BaseModel] = InputSchema

    def _run(self, a: float, b: float) -> float:
        raise NotImplementedError("Subclasses must implement _run")

    async def _arun(self, a: float, b: float) -> float:
        raise NotImplementedError("Async not implemented for this tool")
    
class AddTool(BaseMathTool):
    """Tool that adds two numbers together."""
    name: str = "add_tool"
    description: str = "Adds two numbers together. Example: add_tool(2, 3) -> 5"
    
    def _run(self, a: float, b: float) -> float:
        return a + b  
    

class SubtractTool(BaseMathTool):
    """Tool that subtracts two numbers."""
    name: str = "subtract_tool"
    description: str = "Subtracts b from a. Example: subtract_tool(5, 2) -> 3"
    
    def _run(self, a: float, b: float) -> float:
        return a - b

class MultiplyTool(BaseMathTool):
    """Tool that multiplies two numbers."""
    name: str = "multiply_tool"
    description: str = "Multiplies two numbers. Example: multiply_tool(3, 4) -> 12"
    
    def _run(self, a: float, b: float) -> float:
        return a * b

class DivideTool(BaseMathTool):
    """Tool that divides two numbers."""
    name: str = "divide_tool"
    description: str = "Divides a by b. Returns error if b=0. Example: divide_tool(10, 2) -> 5"
    
    def _run(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b



