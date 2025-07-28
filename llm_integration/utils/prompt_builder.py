
# utils/prompt_builder.py
from typing import Dict, List
import json

class PromptBuilder:
    """
    Constructs well-formatted prompts for Gemini based on retrieved data.
    Implements different prompt templates for different query types.
    """
    
    SYSTEM_PROMPT = """You are a helpful customer support assistant for a business. 
    Use the provided context to answer customer questions accurately and concisely.
    If you don't know the answer, say you don't know - don't make up information.
    Be polite and professional in all responses."""
    
    @classmethod
    def build_faq_prompt(cls, customer_message: str, faqs: List[Dict]) -> Dict:
        """Build prompt for FAQ questions"""
        context = "Relevant FAQs:\n"
        for faq in faqs:
            context += f"Q: {faq['question']}\nA: {faq['answer']}\nCategory: {faq['category']}\n\n"
        
        return {
            "system_instruction": cls.SYSTEM_PROMPT,
            "user_message": customer_message,
            "context": context,
            "instructions": "Answer the customer's question using the provided FAQs. "
                           "If multiple FAQs are relevant, summarize the key points. "
                           "Mention if the answer comes from a specific FAQ category."
        }
    
    @classmethod
    def build_product_prompt(cls, customer_message: str, products: List[Dict]) -> Dict:
        """Build prompt for product questions"""
        context = "Available Products:\n"
        for product in products:
            context += (f"Name: {product['name']}\n"
                       f"Description: {product['description']}\n"
                       f"Price: ${product['price']:.2f}\n"
                       f"Stock: {product['stock']}\n"
                       f"Category: {product['category']}\n\n")
        
        return {
            "system_instruction": cls.SYSTEM_PROMPT,
            "user_message": customer_message,
            "context": context,
            "instructions": "Provide information about the requested products. "
                          "Include pricing and availability details. "
                          "Be clear about any stock limitations."
        }
    
    @classmethod
    def build_service_prompt(cls, customer_message: str, services: List[Dict]) -> Dict:
        """Build prompt for service questions"""
        context = "Available Services:\n"
        for service in services:
            context += (f"Name: {service['name']}\n"
                       f"Description: {service['description']}\n"
                       f"Base Price: ${service['base_price']:.2f}\n"
                       f"Duration: {service['duration']} minutes\n")
            if service.get('hourly_rate'):
                context += f"Hourly Rate: ${service['hourly_rate']:.2f}\n"
            context += "\n"
        
        return {
            "system_instruction": cls.SYSTEM_PROMPT,
            "user_message": customer_message,
            "context": context,
            "instructions": "Provide information about the requested services. "
                          "Include pricing, duration, and any other relevant details. "
                          "You may calculate approximate costs if duration is provided."
        }
    
    @classmethod
    def build_hours_prompt(cls, customer_message: str, hours: List[Dict]) -> Dict:
        """Build prompt for business hours questions"""
        open_days = [h for h in hours if not h['is_closed']]
        closed_days = [h['day'] for h in hours if h['is_closed']]
        
        context = "Business Hours:\n"
        for day in open_days:
            context += (f"{day['day']}: {day['open_time']} - {day['close_time']}\n")
        if closed_days:
            context += f"\nClosed on: {', '.join(closed_days)}\n"
        
        return {
            "system_instruction": cls.SYSTEM_PROMPT,
            "user_message": customer_message,
            "context": context,
            "instructions": "Provide the business hours information clearly. "
                          "Highlight any days when the business is closed. "
                          "If the customer asks about today's hours, calculate accordingly."
        }
    
    @classmethod
    def build_combined_prompt(cls, customer_message: str, context_data: Dict) -> Dict:
        """Build a prompt when multiple context types are available"""
        context_parts = []
        
        if 'faqs' in context_data and context_data['faqs']:
            context_parts.append("Relevant FAQs:")
            for faq in context_data['faqs']:
                context_parts.append(f"Q: {faq['question']}\nA: {faq['answer']}")
        
        if 'products' in context_data and context_data['products']:
            context_parts.append("\nRelevant Products:")
            for product in context_data['products']:
                context_parts.append(
                    f"{product['name']} (${product['price']:.2f}): {product['description']}"
                )
        
        if 'services' in context_data and context_data['services']:
            context_parts.append("\nRelevant Services:")
            for service in context_data['services']:
                context_parts.append(
                    f"{service['name']} (${service['base_price']:.2f}): {service['description']}"
                )
        
        if 'hours' in context_data and context_data['hours']:
            context_parts.append("\nBusiness Hours:")
            for day in context_data['hours']:
                if not day['is_closed']:
                    context_parts.append(f"{day['day']}: {day['open_time']} - {day['close_time']}")
        
        return {
            "system_instruction": cls.SYSTEM_PROMPT,
            "user_message": customer_message,
            "context": "\n".join(context_parts),
            "instructions": "The customer has asked a general question. "
                          "Use all available context to provide a comprehensive answer. "
                          "Organize information clearly by category (FAQs, Products, Services, Hours)."
        }














# apps/llm_integration/utils/prompt_builder.py
# from typing import Dict, List
# from django.conf import settings

# class PromptBuilder:
#     TEMPLATES = {
#         'system': settings.LLM_SYSTEM_PROMPT,
#         'faq': "Answer using these FAQs:\n{context}\n\nUser Question: {message}",
#         'product': "Products matching query:\n{context}\n\nUser Question: {message}",
#         'service': "Available services:\n{context}\n\nUser Question: {message}"
#     }

#     def build_prompt(self, message: str, context: Dict) -> Dict:
#         prompt_type = self._determine_prompt_type(message, context)
#         return {
#             'type': prompt_type,
#             'system': self.TEMPLATES['system'],
#             'context': self._format_context(prompt_type, context),
#             'message': message
#         }

#     def compile_prompt(self, prompt: Dict) -> str:
#         return self.TEMPLATES[prompt['type']].format(
#             context=prompt['context'],
#             message=prompt['message']
#         )