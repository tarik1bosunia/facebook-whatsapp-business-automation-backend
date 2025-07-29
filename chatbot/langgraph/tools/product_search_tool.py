from langchain_core.tools import BaseTool
from typing import List, Type, Optional
import logging
from pydantic import BaseModel, Field
from django.db.models import Q
from business.models import Product
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()

class ProductSearchTool(BaseTool):
    """Tool that searches for products in the database by name, price range, or category."""
    
    name: str = "product_search_tool"
    description: str = (
        "Search products in the database by name, price range, or category. "
        "For product technical questions, use the product_faq_search_tool instead. "
        "Examples: 'iphone', 'price < 1300', 'category:electronics'"
    )
    
    class InputSchema(BaseModel):
        query: str = Field(..., description="Search query (name, price expression, or category)")
        user_id: Optional[int] = Field(None, description="Optional user ID to filter by business owner")
        limit: Optional[int] = Field(10, description="Maximum number of results to return")
    
    args_schema: Type[BaseModel] = InputSchema
    
    def _run(self, query: str, user_id: Optional[int] = None, limit: int = 10) -> str:
        """Search products in the database"""
        try:
            query = query.lower().strip()
            results = self._search_products(query, user_id, limit)
            return self._format_results(results, query)
        except Exception as e:
            logger.error(f"Product search failed for query '{query}': {str(e)}")
            return f"Error processing your query: {str(e)}"

    def _search_products(self, query: str, user_id: Optional[int], limit: int) -> List[Product]:
        """Handle the actual product search logic"""
        queryset = Product.objects.select_related('category').all()
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        if query.startswith('price'):
            return self._search_by_price(queryset, query, limit)
        elif query.startswith('category:'):
            category_name = query.replace('category:', '').strip()
            return self._search_by_category(queryset, category_name, limit)
        else:
            return self._search_by_name(queryset, query, limit)

    def _search_by_price(self, queryset, query: str, limit: int) -> List[Product]:
        """Search products by price range"""
        parts = query.split()
        if len(parts) != 3 or parts[1] not in ["<", ">", "=", "<=", ">="]:
            raise ValueError("Invalid price query format. Use: price <|>|<=|>=|= value")
        
        try:
            price_value = float(parts[2])
            
            if parts[1] == "<":
                return list(queryset.filter(price__lt=price_value).order_by('price')[:limit])
            elif parts[1] == "<=":
                return list(queryset.filter(price__lte=price_value).order_by('price')[:limit])
            elif parts[1] == ">":
                return list(queryset.filter(price__gt=price_value).order_by('-price')[:limit])
            elif parts[1] == ">=":
                return list(queryset.filter(price__gte=price_value).order_by('-price')[:limit])
            else:  # "="
                return list(queryset.filter(price=price_value).order_by('name')[:limit])
        except ValueError:
            raise ValueError("Invalid price value. Must be a number")

    def _search_by_name(self, queryset, query: str, limit: int) -> List[Product]:
        """Search products by name or description"""
        return list(queryset.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).order_by('-stock', 'price')[:limit])

    def _search_by_category(self, queryset, category_name: str, limit: int) -> List[Product]:
        """Search products by category name"""
        return list(queryset.filter(
            Q(category__name__icontains=category_name)
        ).order_by('-stock', 'price')[:limit])

    def _format_results(self, results: List[Product], query: str) -> str:
        """Format the search results"""
        if not results:
            return f"No products found matching '{query}'"
        
        formatted = [f"Found {len(results)} products matching '{query}':"]
        
        for product in results:
            category = product.category.name if product.category else "Uncategorized"
            stock_status = "In Stock" if product.stock > 0 else "Out of Stock"
            
            formatted.append(
                f"\n- {product.name} (${product.price:.2f}) "
                f"\n  Category: {category} | {stock_status} | Available: {product.stock}"
                f"\n  Description: {product.description[:100]}{'...' if len(product.description) > 100 else ''}"
                f"\n  ID: {product.id}"
            )
        
        return "\n".join(formatted)