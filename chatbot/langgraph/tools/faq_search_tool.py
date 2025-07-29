from langchain_core.tools import BaseTool
from typing import List, Type, Optional, Dict, Any
from pydantic import BaseModel, Field
from django.db.models import Q
from knowledge_base.models import FAQ
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class SearchMode(str, Enum):
    """Search mode options for FAQ search."""
    STANDARD = "standard"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"

class FAQSearchTool(BaseTool):
    """
    Enhanced FAQ search tool for business knowledge bases with multiple search modes.
    
    Features:
    - Standard keyword search
    - Category filtering
    - Search mode selection
    - Result relevance scoring
    - Smart answer truncation
    
    Example queries:
    - "return policy for electronics"
    - "category:shipping duration"
    - "how to process refunds"
    """

    name: str = "enhanced_business_faq_search"
    description: str = (
        "Advanced FAQ search tool for business knowledge bases. "
        "Supports keyword search, category filtering, and multiple search modes. "
        "Use 'category:<name>' to filter by category. "
        "Results include relevance scores and smart-truncated answers."
    )

    class InputSchema(BaseModel):
        query: str = Field(
            ...,
            description="Search query or 'category:<name>' to filter by category."
        )
        limit: Optional[int] = Field(
            5,
            description="Maximum number of results to return (1-10).",
            ge=1,
            le=10
        )
        mode: Optional[SearchMode] = Field(
            SearchMode.STANDARD,
            description="Search mode: 'standard', 'semantic', or 'hybrid'."
        )
        min_relevance: Optional[float] = Field(
            0.3,
            description="Minimum relevance score threshold (0.0-1.0).",
            ge=0.0,
            le=1.0
        )
        include_metadata: Optional[bool] = Field(
            True,
            description="Include category and relevance metadata in results."
        )

    args_schema: Type[BaseModel] = InputSchema

    def _run(
        self,
        query: str,
        limit: int = 5,
        mode: SearchMode = SearchMode.STANDARD,
        min_relevance: float = 0.3,
        include_metadata: bool = True
    ) -> str:
        """
        Execute FAQ search with enhanced options.
        
        Args:
            query: Search text or category filter
            limit: Maximum results to return (1-10)
            mode: Search algorithm to use
            min_relevance: Minimum match quality threshold
            include_metadata: Whether to show category/scores
            
        Returns:
            Formatted search results or error message
        """
        try:
            query = query.strip()
            results = self._search_faqs(
                query=query,
                limit=limit,
                mode=mode,
                min_relevance=min_relevance
            )
            return self._format_results(
                results=results,
                query=query,
                include_metadata=include_metadata
            )
        except Exception as e:
            logger.error(
                f"FAQ search failed for query '{query}': {str(e)}",
                exc_info=True,
                extra={
                    'query': query,
                    'limit': limit,
                    'mode': mode
                }
            )
            return f"⚠️ Error processing your query: {str(e)}"

    def _search_faqs(
        self,
        query: str,
        limit: int,
        mode: SearchMode,
        min_relevance: float
    ) -> List[Dict[str, Any]]:
        """Core search logic with multiple modes."""
        # Category-specific search
        if query.lower().startswith('category:'):
            category_name = query[9:].strip()
            return self._search_by_category(category_name, limit)
        
        # Determine search mode
        if mode == SearchMode.SEMANTIC:
            return self._semantic_search(query, limit, min_relevance)
        elif mode == SearchMode.HYBRID:
            return self._hybrid_search(query, limit, min_relevance)
        else:
            return self._standard_search(query, limit)

    def _standard_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Traditional keyword-based search."""
        faqs = FAQ.objects.filter(
            Q(question__icontains=query) | 
            Q(answer__icontains=query) |
            Q(keywords__icontains=query)
        ).select_related('category').order_by('-last_updated')[:limit]
        
        return [self._prepare_faq_result(faq) for faq in faqs]

    def _semantic_search(self, query: str, limit: int, min_score: float) -> List[Dict[str, Any]]:
        """Semantic/vector search implementation."""
        # Placeholder for actual vector search implementation
        # In practice, you would use a vector DB or embedding service
        from django.db.models import F, ExpressionWrapper, FloatField
        from django.db.models.functions import Greatest
        
        # Simulate semantic scoring
        faqs = FAQ.objects.annotate(
            question_score=ExpressionWrapper(
                Greatest(0.1, 0.8 - (0.1 * F('question__search'))),
                output_field=FloatField()
            ),
            answer_score=ExpressionWrapper(
                Greatest(0.1, 0.7 - (0.1 * F('answer__search'))),
                output_field=FloatField()
            ),
            relevance=ExpressionWrapper(
                (F('question_score') * 0.6 + F('answer_score') * 0.4),
                output_field=FloatField()
            )
        ).filter(
            relevance__gte=min_score
        ).select_related('category').order_by('-relevance')[:limit]
        
        return [self._prepare_faq_result(faq) for faq in faqs]

    def _hybrid_search(self, query: str, limit: int, min_score: float) -> List[Dict[str, Any]]:
        """Combine keyword and semantic search."""
        keyword_results = self._standard_search(query, limit)
        semantic_results = self._semantic_search(query, limit, min_score)
        
        # Combine and deduplicate results
        seen_ids = set()
        combined = []
        
        for result in semantic_results + keyword_results:
            if result['id'] not in seen_ids:
                combined.append(result)
                seen_ids.add(result['id'])
                if len(combined) >= limit:
                    break
                    
        return combined

    def _search_by_category(self, category_name: str, limit: int) -> List[Dict[str, Any]]:
        """Search within a specific category."""
        faqs = FAQ.objects.filter(
            Q(category__name__icontains=category_name) |
            Q(category__slug__iexact=category_name)
        ).select_related('category').order_by('-view_count')[:limit]
        
        return [self._prepare_faq_result(faq) for faq in faqs]

    def _prepare_faq_result(self, faq: FAQ) -> Dict[str, Any]:
        """Prepare standardized result dictionary."""
        return {
            'id': faq.id,
            'question': faq.question,
            'answer': faq.answer,
            'category': faq.category.name if faq.category else None,
            'relevance': getattr(faq, 'relevance', 0.8),  # Default for non-scored results
            'last_updated': faq.last_updated,
            'view_count': faq.view_count
        }

    def _format_results(
        self,
        results: List[Dict[str, Any]],
        query: str,
        include_metadata: bool
    ) -> str:
        """Format results for LLM consumption."""
        if not results:
            return f"🔍 No FAQs found matching '{query}'"
        
        output = [f"📚 Found {len(results)} relevant FAQs:"]
        
        for result in results:
            output.append(f"\n❓ {result['question']}")
            
            # Smart answer truncation
            answer = result['answer']
            if len(answer) > 300:
                answer = answer[:300] + "... [truncated]"
            output.append(f"💡 {answer}")
            
            if include_metadata:
                meta = []
                if result['category']:
                    meta.append(f"🏷️ {result['category']}")
                if 'relevance' in result:
                    meta.append(f"⭐ {result['relevance']:.2f}")
                if meta:
                    output.append(" | ".join(meta))
            
            output.append(f"\n{'━'*40}")
        
        return "\n".join(output)

    def _arun(self, *args, **kwargs):
        """Async version not implemented."""
        raise NotImplementedError("Async operation not supported")