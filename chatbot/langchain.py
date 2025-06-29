import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from django.conf import settings

from django.db.models import Q
from knowledge_base.models import FAQ, Category
from .models import AIConfiguration, ToneChoices

class LLMResponseGenerator:
    def __init__(self, ai_config: AIConfiguration):
        self.ai_config = ai_config
        self.llm = self._initialize_llm()
        self.faq_search = FAQVectorSearch()
        self.prompt_template = self._create_prompt_template()
        self.chain = self.prompt_template | self.llm | StrOutputParser()

    def _initialize_llm(self):
        """Initialize the appropriate LLM based on configuration"""
        if self.ai_config.ai_model in ['gemini-2.0-flash', 'gemini-ultra']:
            return ChatGoogleGenerativeAI(
                model=self.ai_config.ai_model,
                google_api_key=self.ai_config.api_key or settings.GEMINI_API_KEY,
                temperature=0.7
            )
        elif self.ai_config.ai_model == 'custom':
            # Implement your custom model here
            raise NotImplementedError("Custom model implementation required")
        else:
            raise ValueError(f"Unsupported model: {self.ai_config.ai_model}")
        
    def _get_relevant_faqs(self, user_input, threshold=0.3):
        """
        Retrieve relevant FAQs using simple similarity search
        For production, consider using vector similarity search
        """
        # Split input into keywords
        keywords = user_input.lower().split()
        queries = [Q(question__icontains=kw) | Q(answer__icontains=kw) for kw in keywords]
        
        # Start with empty query
        query = Q()
        
        # Combine queries with OR
        for q in queries:
            query |= q
        
        return FAQ.objects.filter(query).distinct()[:5]  # Return top 5 matches    

    def _create_prompt_template(self):
        """Enhanced prompt template with FAQ context"""
        tone_mapping = {
            ToneChoices.FRIENDLY: "Use a friendly and casual tone in your response.",
            ToneChoices.PROFESSIONAL: "Use a professional tone in your response.",
            ToneChoices.FORMAL: "Use a formal tone in your response.",
            ToneChoices.HELPFUL: "Use a helpful and informative tone in your response.",
        }
        
        tone_instruction = tone_mapping.get(self.ai_config.response_tone, "")
        
        return ChatPromptTemplate.from_messages([
            ("system", f"""
            {self.ai_config.brand_persona}
            
            Additional Instructions:
            - {tone_instruction}
            - Be concise and to the point
            - Always maintain a positive attitude
            - If relevant information exists in our FAQ, use it to craft your response
            """),
            ("human", "{user_input}"),
            ("system", """
            Context:
            - FAQ Knowledge Base: {faq_context}
            """),
        ])
    
    def _get_relevant_faqs(self, user_input):
        """Use vector search for FAQ retrieval"""
        results = self.faq_search.search(user_input)
        return [
            FAQ.objects.get(id=result['id'])
            for result in results
            if result['score'] > 0.5  # Only include reasonably good matches
        ][:3]  # Return top 3 matches
    
    

    def generate_response(self, user_input, chat_history=None):
        """Generate response with FAQ context"""
        # Get relevant FAQs
        relevant_faqs = self._get_relevant_faqs(user_input)
        faq_context = "\n\n".join(
            [f"Q: {faq.question}\nA: {faq.answer}" for faq in relevant_faqs]
        ) if relevant_faqs else "No relevant FAQs found"
        
        context = {
            "user_input": user_input,
            "faq_context": faq_context,
        }
        
        if chat_history and self.ai_config.learn_from_history:
            context["chat_history"] = "\n".join(
                [f"{msg['sender']}: {msg['message']}" for msg in chat_history]
            )
        
        return self.chain.invoke(context)
    

# from django.core.cache import cache

# class LLMResponseGenerator:
#     # ... existing code ...
    
#     def generate_response(self, user_input, chat_history=None):
#         """Generate response with caching"""
#         cache_key = f"llm_response:{self.ai_config.user.id}:{hash(user_input)}"
#         cached_response = cache.get(cache_key)
        
#         if cached_response:
#             return cached_response
            
#         context = {"user_input": user_input}
        
#         if chat_history and self.ai_config.learn_from_history:
#             context["chat_history"] = "\n".join(
#                 [f"{msg['sender']}: {msg['message']}" for msg in chat_history]
#             )
        
#         response = self.chain.invoke(context)
#         cache.set(cache_key, response, timeout=60*15)  # Cache for 15 minutes
#         return response


# from tenacity import retry, stop_after_attempt, wait_exponential
# from langchain_core.exceptions import LLMError

# class LLMResponseGenerator:
#     # ... existing code ...
    
#     @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
#     def _safe_generate(self, context):
#         try:
#             return self.chain.invoke(context)
#         except LLMError as e:
#             # Log error and return fallback response
#             logger.error(f"LLM Error: {str(e)}")
#             return "I'm having trouble generating a response right now. Please try again later."
    
#     def generate_response(self, user_input, chat_history=None):
#         try:
#             # ... existing context preparation ...
#             return self._safe_generate(context)
#         except Exception as e:
#             logger.error(f"Unexpected error: {str(e)}")
#             return "Sorry, I encountered an unexpected error while processing your request."


from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import numpy as np

class FAQVectorSearch:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = None
        
    def initialize_vectorstore(self):
        """Initialize FAQ vector store"""
        faqs = FAQ.objects.all()
        texts = [f"Q: {faq.question}\nA: {faq.answer}" for faq in faqs]
        metadatas = [{"id": faq.id, "category": faq.category.name} for faq in faqs]
        
        if texts:
            self.vectorstore = FAISS.from_texts(
                texts, 
                embedding=self.embeddings,
                metadatas=metadatas
            )
    
    def search(self, query, k=3):
        """Search FAQs using vector similarity"""
        if not self.vectorstore:
            self.initialize_vectorstore()
        
        if not self.vectorstore:
            return []
        
        docs = self.vectorstore.similarity_search(query, k=k)
        return [{
            'id': doc.metadata['id'],
            'question': FAQ.objects.get(id=doc.metadata['id']).question,
            'answer': FAQ.objects.get(id=doc.metadata['id']).answer,
            'score': self._calculate_score(query, doc.page_content)
        } for doc in docs]
    
    def _calculate_score(self, query, text):
        """Calculate similarity score (simplified example)"""
        query_embedding = self.embeddings.embed_query(query)
        text_embedding = self.embeddings.embed_query(text)
        return np.dot(query_embedding, text_embedding)
    
    