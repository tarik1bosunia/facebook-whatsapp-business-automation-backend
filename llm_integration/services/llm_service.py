from typing import Optional, Dict, Any
from google.api_core import retry
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from django.conf import settings
from ..utils.query_utils import DatabaseQueryTool
from ..utils.prompt_builder import PromptBuilder
import logging
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

class LLMService:
    """
    Service class for handling LLM interactions with Gemini using LangChain.
    Handles querying relevant data, building prompts, and generating responses.
    """
    
    def __init__(self, user):
        self.user = user
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7,
            max_output_tokens=2048,
            top_k=40,
            top_p=0.95
        )
    
    @retry.Retry(
        initial=1.0,
        maximum=10.0,
        multiplier=2.0,
        deadline=30.0,
        predicate=retry.if_exception_type(
            Exception  # Adjust with specific exceptions you want to retry
        )
    )
    async def generate_response_async(self, customer_message: str) -> Dict[str, Any]:
        """
        Main method to generate a response to a customer message.
        Uses async for better performance with external API calls.
        """
        # Step 1: Query relevant data
        context_data = await self._gather_context(customer_message)
        
        # Step 2: Build appropriate prompt
        prompt = self._build_prompt(customer_message, context_data)
        
        # Step 3: Generate response from LLM
        response = await self._call_llm(prompt)
        
        # Step 4: Format and return response
        return {
            'response': response,
            'context_used': self._summarize_context_usage(context_data),
            'prompt': prompt  # For debugging purposes
        }
    
    async def _gather_context(self, customer_message: str) -> Dict[str, Any]:
        """Gather all potentially relevant context from database"""
        faqs = await sync_to_async(DatabaseQueryTool.query_faqs)(self.user, customer_message)
        products = await sync_to_async(DatabaseQueryTool.query_products)(self.user, customer_message)
        services = await sync_to_async(DatabaseQueryTool.query_services)(self.user, customer_message)
        hours = await sync_to_async(DatabaseQueryTool.query_business_hours)(self.user)
        
        return {
            'faqs': faqs,
            'products': products,
            'services': services,
            'hours': hours
        }
    
    def _build_prompt(self, customer_message: str, context_data: Dict) -> Dict:
        """Determine which prompt template to use based on available context"""
        message_lower = customer_message.lower()
        
        # Check for FAQ-like questions
        if any(word in message_lower for word in ['what', 'how', 'why', 'when', 'where', 'can i', 'do you']):
            if context_data['faqs']:
                return PromptBuilder.build_faq_prompt(customer_message, context_data['faqs'])
        
        # Check for product queries
        if any(word in message_lower for word in ['product', 'item', 'buy', 'purchase', 'price', 'stock']):
            if context_data['products']:
                return PromptBuilder.build_product_prompt(customer_message, context_data['products'])
        
        # Check for service queries
        if any(word in message_lower for word in ['service', 'appointment', 'book', 'schedule', 'reserve']):
            if context_data['services']:
                return PromptBuilder.build_service_prompt(customer_message, context_data['services'])
        
        # Check for hours queries
        if any(word in message_lower for word in ['open', 'close', 'hour', 'time', 'available', 'when are you']):
            if context_data['hours']:
                return PromptBuilder.build_hours_prompt(customer_message, context_data['hours'])
        
        # Default to combined prompt
        return PromptBuilder.build_combined_prompt(customer_message, context_data)
    
    async def _call_llm(self, prompt: Dict) -> str:
        """Make the actual API call using LangChain's ChatGoogleGenerativeAI"""
        try:
            # Create LangChain messages
            messages = [
                SystemMessage(content=prompt['system_instruction']),
                HumanMessage(content=(
                    f"Context:\n{prompt['context']}\n\n"
                    f"Additional Instructions: {prompt['instructions']}\n\n"
                    f"Customer Message: {prompt['user_message']}"
                ))
            ]
            
            # Invoke the LLM asynchronously
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}", exc_info=True)
            return ("I'm sorry, I'm having trouble processing your request right now. "
                   "Please try again later or contact our support team directly.")
    
    def _summarize_context_usage(self, context_data: Dict) -> Dict:
        """Create a summary of what context was used for logging/analytics"""
        return {
            'faqs_used': len(context_data.get('faqs', [])),
            'products_used': len(context_data.get('products', [])),
            'services_used': len(context_data.get('services', [])),
            'hours_used': len(context_data.get('hours', [])) if context_data.get('hours') else 0
        }