# utils/query_utils.py
from typing import List, Dict, Optional, Set, Union
from django.db.models import Q, QuerySet, Count, F
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank
)
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from account.models import User
import logging
import requests  # For API-based embeddings

logger = logging.getLogger(__name__)

class DatabaseQueryTool:
    """
    Optimized query utility for large-scale datasets with millions of records.
    Implements pagination, caching, and advanced search techniques.
    """
    
    MAX_RESULTS = 5  # Default number of results to return
    SEARCH_SCORE_THRESHOLD = 0.3
    
    @staticmethod
    def query_faqs(user: User, query_text: str, threshold: float = SEARCH_SCORE_THRESHOLD, 
                  limit: int = MAX_RESULTS) -> List[Dict[str, Union[str, float]]]:
        """
        Vector similarity search with pgvector for large FAQ datasets.
        Falls back to text search if vector search not available.
        """
        from knowledge_base.models import FAQ
        
        try:
            # Try vector search first if available
            from pgvector.django import L2Distance
            embedded_query = DatabaseQueryTool._get_embedding(query_text)
            if embedded_query:
                results = (
                    FAQ.objects
                    .annotate(distance=L2Distance('embedding', embedded_query))
                    .filter(category__user=user, distance__lt=threshold)
                    .order_by('distance')[:limit]
                )
                return [{
                    'question': faq.question,
                    'answer': faq.answer,
                    'score': 1 - float(faq.distance)
                } for faq in results]
        except ImportError:
            logger.warning("pgvector not available, falling back to text search")
        
        # Fallback to optimized text search
        cache_key = f"faqs_{user.id}_{hash(query_text)}"
        cached_results = cache.get(cache_key)
        if cached_results:
            return cached_results[:limit]
            
        query_words = set(query_text.lower().split())
        if not query_words:
            return []
            
        # Create search conditions for each word
        conditions = Q()
        for word in query_words:
            conditions |= Q(question__icontains=word) | Q(answer__icontains=word)
            
        results = (
            FAQ.objects
            .filter(category__user=user)
            .filter(conditions)
            .annotate(match_count=Count('id'))  # Simple relevance metric
            .order_by('-match_count')[:limit*5]  # Get more then filter
        )
        
        # Score and filter results
        scored_results = []
        for faq in results:
            question_words = set(faq.question.lower().split())
            answer_words = set(faq.answer.lower().split())
            score = max(
                len(query_words & question_words) / len(query_words),
                len(query_words & answer_words) / len(query_words)
            )
            if score >= threshold:
                scored_results.append({
                    'question': faq.question,
                    'answer': faq.answer,
                    'score': score
                })
        
        # Cache and return top results
        final_results = sorted(scored_results, key=lambda x: x['score'], reverse=True)[:limit]
        cache.set(cache_key, final_results, timeout=60*15)  # 15 minute cache
        return final_results

    
    @staticmethod
    def query_products(user: User, query_text: str, limit: int = MAX_RESULTS) -> List[Dict]:
        """
        Optimized product search with:
        - Full-text search if available
        - Field weighting
        - Popularity boosting
        """
        from business.models import Product
        
        # Use database-specific optimizations
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
            # PostgreSQL full-text search
            return list(
                Product.objects
                .filter(user=user)
                .annotate(
                    search=SearchVector('name', weight='A') + 
                    SearchVector('description', weight='B') +
                    SearchVector('category__name', weight='C')
                )
                .filter(search=SearchQuery(query_text))
                .annotate(rank=SearchRank(F('search'), SearchQuery(query_text)))
                .order_by('-rank', '-popularity_score')[:limit]
                .values('id', 'name', 'description', 'price', 'stock')
            )
        else:
            # Generic search for other databases
            query_words = query_text.split()
            conditions = Q()
            for word in query_words:
                conditions |= (
                    Q(name__icontains=word) |
                    Q(description__icontains=word) |
                    Q(category__name__icontains=word)
                )
            
            return list(
                Product.objects
                .filter(user=user)
                .filter(conditions)
                .order_by('-popularity_score', '-stock')[:limit]
                .values('id', 'name', 'description', 'price', 'stock')
            )

    @staticmethod
    def query_services(user: User, query_text: str, limit: int = MAX_RESULTS) -> List[Dict]:
        """Optimized service search with booking availability consideration"""
        from business.models import Service
        
        # Get popular services that match query
        base_query = (
            Service.objects
            .filter(user=user)
            .filter(
                Q(name__icontains=query_text) |
                Q(description__icontains=query_text))
        )
        



    @staticmethod
    def _get_embedding(text: str) -> Optional[List[float]]:
        """Generate embedding using available services"""
        try:
            # Option 1: Use OpenAI embeddings
            if hasattr(settings, 'OPENAI_API_KEY'):
                return DatabaseQueryTool._get_openai_embedding(text)
            
            # Option 2: Use HuggingFace embeddings
            elif hasattr(settings, 'HF_API_KEY'):
                return DatabaseQueryTool._get_hf_embedding(text)
            
            # Option 3: Use Sentence Transformers (local)
            try:
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer('all-MiniLM-L6-v2')
                return model.encode(text).tolist()
            except ImportError:
                pass
                
            logger.warning("No embedding service configured")
            return None
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            return None

    @staticmethod
    def _get_openai_embedding(text: str) -> Optional[List[float]]:
        """Get embedding from OpenAI API"""
        try:
            import openai
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {str(e)}")
            return None

    @staticmethod
    def _get_hf_embedding(text: str) -> Optional[List[float]]:
        """Get embedding from HuggingFace API"""
        try:
            API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
            headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}
            response = requests.post(
                API_URL,
                headers=headers,
                json={"inputs": text}
            )
            return response.json()
        except Exception as e:
            logger.error(f"HuggingFace embedding failed: {str(e)}")
            return None