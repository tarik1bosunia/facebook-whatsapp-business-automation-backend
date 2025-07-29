from langchain_core.tools import BaseTool
from typing import List, Type, Optional
from pydantic import BaseModel, Field
from django.db.models import Q
from business.models import ProductFAQ
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class ProductFAQSearchTool(BaseTool):
    """Tool specifically for searching FAQs related to products."""
    
    name: str = "product_faq_search_tool"
    description: str = (
        "Search product-specific frequently asked questions. "
        "Use for technical questions, specifications, or troubleshooting about products. "
        "Examples: 'iPhone battery life', 'how to pair headphones', 'warranty coverage'"
    )
    
    class InputSchema(BaseModel):
        query: str = Field(..., description="Search query for product FAQs")
        product_id: Optional[int] = Field(None, description="Optional specific product ID to filter")
        user_id: Optional[int] = Field(None, description="Optional user ID to filter by business owner")
        limit: Optional[int] = Field(5, description="Maximum number of FAQ results to return")
        include_product_info: Optional[bool] = Field(True, description="Whether to include full product details")
    
    args_schema: Type[BaseModel] = InputSchema
    
    def _run(self, query: str, product_id: Optional[int] = None, 
             user_id: Optional[int] = None, limit: int = 5,
             include_product_info: bool = True) -> str:
        try:
            query = query.lower().strip()
            results = self._search_product_faqs(query, product_id, user_id, limit)
            return self._format_results(results, query, include_product_info)
        except Exception as e:
            logger.error(f"Product FAQ search failed for query '{query}': {str(e)}")
            return f"Error searching product FAQs: {str(e)}"

    def _search_product_faqs(self, query: str, product_id: Optional[int],
                           user_id: Optional[int], limit: int) -> List[ProductFAQ]:
        queryset = ProductFAQ.objects.select_related('product', 'product__category')
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if user_id:
            queryset = queryset.filter(product__user_id=user_id)
            
        return list(queryset.filter(
            Q(question__icontains=query) | Q(answer__icontains=query)
        ).order_by('-product__stock')[:limit])

    def _format_results(self, faqs: List[ProductFAQ], query: str, include_product_info: bool) -> str:
        if not faqs:
            return f"No product FAQs found matching '{query}'"
            
        results = [f"Found {len(faqs)} product FAQ matches:"]
        
        for faq in faqs:
            results.append(f"\nQ: {faq.question}")
            results.append(f"A: {faq.answer}")
            
            if include_product_info:
                product = faq.product
                stock_status = "In Stock" if product.stock > 0 else "Out of Stock"
                results.append(
                    f"\nRelated Product: {product.name} (ID: {product.id})"
                    f"\nPrice: ${product.price:.2f} | {stock_status} | Available: {product.stock}"
                )
            results.append(f"\n{'-'*40}")
        
        return "\n".join(results)