# llm_integration/generators/response_generator.py
from typing import List, Dict, Optional
from django.conf import settings
from django.db.models import Q
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
import numpy as np
import logging
logger = logging.getLogger(__name__)


class AIConfiguration:
    """Configuration for AI response generation"""
    def __init__(
        self,
        ai_model: str = 'gemini-pro',
        api_key: str = None,
        response_tone: str = 'professional',
        brand_persona: str = 'helpful assistant',
        learn_from_history: bool = True,
        faq_threshold: float = 0.5
    ):
        self.ai_model = ai_model
        self.api_key = api_key
        self.response_tone = response_tone
        self.brand_persona = brand_persona
        self.learn_from_history = learn_from_history
        self.faq_threshold = faq_threshold



class FAQVectorSearch:
    """Vector search implementation for FAQs"""
    def __init__(self, embeddings: Embeddings = None):
        self.embeddings = embeddings or self._get_default_embeddings()
        self.vector_store = None
        self._initialize_vector_store()

    def _get_default_embeddings(self):
        """Get default embedding model"""
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            return GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=settings.GEMINI_API_KEY
            )
        except ImportError:
            logger.warning("GoogleGenerativeAIEmbeddings not available")
            return None

    def _initialize_vector_store(self):
        """Initialize vector store with FAQs"""
        from knowledge_base.models import FAQ
        faqs = FAQ.objects.all()
        if not faqs:
            return

        texts = [f"Q: {faq.question}\nA: {faq.answer}" for faq in faqs]
        metadatas = [{"id": faq.id} for faq in faqs]

        if self.embeddings:
            self.vector_store = FAISS.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas
            )

    def search(self, query: str, k: int = 3) -> List[Dict]:
        """Search FAQs using vector similarity"""
        if not self.vector_store:
            return []

        try:
            docs = self.vector_store.similarity_search_with_score(query, k=k)
            return [{
                'id': doc.metadata['id'],
                'score': float(1 - score),
                'content': doc.page_content
            } for doc, score in docs]
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            return []
        

class LLMResponseGenerator:
    """Complete response generator with FAQ integration"""
    
    def __init__(self, ai_config: AIConfiguration):
        self.ai_config = ai_config
        self.llm = self._initialize_llm()
        self.faq_search = FAQVectorSearch()
        self.prompt_template = self._create_prompt_template()
        self.chain = self.prompt_template | self.llm | StrOutputParser()

    def _initialize_llm(self):
        """Initialize the appropriate LLM based on configuration"""
        if self.ai_config.ai_model in ['gemini-pro', 'gemini-1.5-flash']:
            return ChatGoogleGenerativeAI(
                model=self.ai_config.ai_model,
                google_api_key=self.ai_config.api_key or settings.GEMINI_API_KEY,
                temperature=0.7
            )
        elif self.ai_config.ai_model.startswith('gpt-'):
            return ChatOpenAI(
                model=self.ai_config.ai_model,
                openai_api_key=self.ai_config.api_key or settings.OPENAI_API_KEY,
                temperature=0.7
            )
        else:
            raise ValueError(f"Unsupported model: {self.ai_config.ai_model}")

    def _create_prompt_template(self):
        """Enhanced prompt template with FAQ context"""
        tone_instructions = {
            'friendly': "Use a friendly and casual tone.",
            'professional': "Use a professional and polite tone.",
            'formal': "Use a formal and precise tone.",
            'helpful': "Use a helpful and informative tone.",
        }
        
        tone = tone_instructions.get(
            self.ai_config.response_tone.lower(),
            tone_instructions['professional']
        )
        
        return ChatPromptTemplate.from_messages([
            ("system", f"""
            You are a customer support assistant for {self.ai_config.brand_persona}.
            
            Guidelines:
            1. {tone}
            2. Be concise and accurate
            3. Maintain positive engagement
            4. Use FAQ context when relevant
            5. Never invent information
            """),
            ("human", "Customer Question: {user_input}"),
            ("system", """
            FAQ Context:
            {faq_context}
            
            Chat History:
            {chat_history}
            """),
        ])

    def _get_relevant_faqs(self, user_input: str) -> List[Dict]:
        """Retrieve relevant FAQs using vector search"""
        results = self.faq_search.search(user_input)
        return [
            result for result in results
            if result['score'] >= self.ai_config.faq_threshold
        ][:3]

    def _format_chat_history(self, chat_history: List[Dict]) -> str:
        """Format chat history for context"""
        if not chat_history or not self.ai_config.learn_from_history:
            return "No previous conversation"
            
        return "\n".join(
            f"{msg.get('sender', 'User')}: {msg.get('message', '')}"
            for msg in chat_history[-5:]  # Last 5 messages
        )

    def generate_response(self, user_input: str, chat_history: List[Dict] = None) -> Dict:
        """
        Generate AI response with context awareness
        Returns:
            {
                "response": str,
                "sources": List[Dict],
                "metadata": Dict
            }
        """
        try:
            # Get relevant FAQs
            faq_results = self._get_relevant_faqs(user_input)
            faq_context = "\n---\n".join(
                [res['content'] for res in faq_results]
            ) if faq_results else "No relevant FAQs found"

            # Prepare context
            context = {
                "user_input": user_input,
                "faq_context": faq_context,
                "chat_history": self._format_chat_history(chat_history)
            }

            # Generate response
            response = self.chain.invoke(context)
            
            return {
                "response": response,
                "sources": faq_results,
                "metadata": {
                    "model": self.ai_config.ai_model,
                    "tone": self.ai_config.response_tone,
                    "context_used": bool(faq_results)
                }
            }

        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return {
                "response": "I'm having trouble generating a response. Please try again later.",
                "error": str(e),
                "sources": []
            }        

