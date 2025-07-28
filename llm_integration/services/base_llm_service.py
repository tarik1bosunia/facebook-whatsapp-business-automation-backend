# apps/llm_integration/services/base_llm_service.py
from abc import ABC, abstractmethod
from typing import Dict, Any
import datetime

class BaseLLMService(ABC):
    @abstractmethod
    async def generate_response(self, customer_message: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def validate_message(self, message: str) -> bool:
        pass

    @staticmethod
    def format_response(response: str, context_used: Dict) -> Dict:
        return {
            'response': response,
            'context_used': context_used,
            'timestamp': datetime.datetime.now().isoformat()
        }