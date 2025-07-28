# apps/llm_integration/services/gemini_service.py
import logging
from typing import Dict
from google.api_core import retry
from google.generativeai import configure, GenerativeModel
from django.conf import settings
from .base_llm_service import BaseLLMService
from apps.llm_integration.utils import QueryUtils, PromptBuilder

logger = logging.getLogger(__name__)

class GeminiService(BaseLLMService):
    def __init__(self, user):
        self.user = user
        configure(api_key=settings.GEMINI_API_KEY)
        self.model = GenerativeModel('gemini-pro')
        self.query_utils = QueryUtils()
        self.prompt_builder = PromptBuilder()

    async def generate_response(self, customer_message: str) -> Dict[str, Any]:
        if not self.validate_message(customer_message):
            return self.format_response("Invalid message format", {})
        
        try:
            context = await self.query_utils.gather_context(self.user, customer_message)
            prompt = self.prompt_builder.build_prompt(customer_message, context)
            response = await self._call_gemini(prompt)
            return self.format_response(response, self.query_utils.summarize_context(context))
        except Exception as e:
            logger.error(f"Gemini error: {str(e)}")
            return self.format_response("I'm having trouble processing your request", {})

    @retry.Retry(deadline=30.0)
    async def _call_gemini(self, prompt: Dict) -> str:
        response = await self.model.generate_content_async(
            self.prompt_builder.compile_prompt(prompt))
        return response.text

    def validate_message(self, message: str) -> bool:
        return len(message.strip()) > 2 and len(message) < 1000