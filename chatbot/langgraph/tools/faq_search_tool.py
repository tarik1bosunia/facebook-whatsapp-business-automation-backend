from langchain_core.tools import BaseTool
from typing import List, Dict, Any, Type, Optional
import logging
from pydantic import BaseModel, Field
from django.db.models import Q
from knowledge_base.models import FAQ, Category
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()

class FAQSearchTool(BaseTool):
    """Tool that searches FAQs in the knowledge base by question, answer, or category."""
    
    name: str = "faq_search_tool"
    description: str = (
        "Search frequently asked questions in the knowledge base. "
        "Examples: 'How to reset password', 'refund policy', 'category:account'"
    )
    
    # Define input schema
    class InputSchema(BaseModel):
        query: str = Field(..., description="Search query (question text, answer text, or category)")
        user_id: Optional[int] = Field(None, description="Optional user ID to filter by business owner")
        limit: Optional[int] = Field(5, description="Maximum number of results to return")
    
    args_schema: Type[BaseModel] = InputSchema
    
    def _run(self, query: str, user_id: Optional[int] = None, limit: int = 5) -> str:
        """Search FAQs in the knowledge base"""
        try:
            query = query.lower().strip()
            results = self._search_faqs(query, user_id, limit)
            return self._format_results(results, query)
        except Exception as e:
            logger.error(f"FAQ search failed for query '{query}': {str(e)}")
            return f"Error processing your query: {str(e)}"

    def _search_faqs(self, query: str, user_id: Optional[int], limit: int) -> List[FAQ]:
        """Handle the actual FAQ search logic"""
        # Start with base queryset
        queryset = FAQ.objects.select_related('category').all()
        
        # Filter by user if specified
        if user_id:
            queryset = queryset.filter(category__user_id=user_id)
        
        # Check for category queries
        if query.startswith('category:'):
            category_name = query.replace('category:', '').strip()
            return self._search_by_category(queryset, category_name, limit)
        # Default to question/answer search
        else:
            return self._search_by_text(queryset, query, limit)

    def _search_by_category(self, queryset, category_name: str, limit: int) -> List[FAQ]:
        """Search FAQs by category name"""
        return list(queryset.filter(
            Q(category__name__icontains=category_name)
        ).order_by('question')[:limit])

    def _search_by_text(self, queryset, query: str, limit: int) -> List[FAQ]:
        """Search FAQs by question or answer text"""
        return list(queryset.filter(
            Q(question__icontains=query) | Q(answer__icontains=query)
        ).order_by('question')[:limit])

    def _format_results(self, results: List[FAQ], query: str) -> str:
        """Format the FAQ search results"""
        if not results:
            return f"No FAQs found matching '{query}'"
        
        formatted = [f"Found {len(results)} FAQs matching '{query}':"]
        
        for faq in results:
            formatted.append(
                f"\nQ: {faq.question}"
                f"\nA: {faq.answer}"
                f"\nCategory: {faq.category.name}"
                f"\n{'-'*40}"
            )
        
        return "\n".join(formatted)