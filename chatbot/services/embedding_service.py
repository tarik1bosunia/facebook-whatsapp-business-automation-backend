from typing import List
from django.conf import settings
# from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEndpointEmbeddings
import logging

logger = logging.getLogger(__name__)


class HuggingFaceEmbeddingService:
    """Production-ready HuggingFace embeddings service"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = cls._initialize_model()
        return cls._instance

    @staticmethod
    def _initialize_model():

        return HuggingFaceEndpointEmbeddings(
            model=settings.EMBEDDING_MODEL,
            task="feature-extraction",
            huggingfacehub_api_token=settings.HUGGINGFACEHUB_API_TOKEN,
            # timeout=120,  # timeout for API calls
        )

        # device = "cuda" if torch.cuda.is_available() else "cpu"
        # return HuggingFaceEmbeddings(
        #     model_name=settings.EMBEDDING_MODEL,
        #     model_kwargs={'device': device},
        #     encode_kwargs={
        #         'normalize_embeddings': True,
        #         'batch_size': 32  # Optimized for throughput
        #     }
        # )

    def embed_text(self, text: str) -> List[float]:
        """Get embeddings for a single text with proper validation"""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            return self.model.embed_query(text[:8192])  # Safe truncation
        except Exception as e:
            logger.error(f"Embedding failed for text: {e}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Batch process multiple texts efficiently"""
        if not texts:
            return []
        
        try:
            # Process in chunks to avoid hitting API limits
            batch_size = 32  # Adjust based on your API plan
            results = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                results.extend(self.model.embed_documents([t[:8192] for t in batch]))
            return results
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            raise
