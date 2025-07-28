from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from django.db.models import Q
from business.models import Product
import logging

logger = logging.getLogger(__name__)

class ProductSearchInput(BaseModel):
    search_term: Optional[str] = Field(None, description="Text to search in products")
    category_id: Optional[int] = Field(None, description="Filter by category ID")
    max_price: Optional[float] = Field(None, description="Maximum price filter")
    min_price: Optional[float] = Field(None, description="Minimum price filter")
    in_stock_only: bool = Field(False, description="Only show in-stock items")
    limit: int = Field(10, description="Maximum results to return")

@tool(args_schema=ProductSearchInput)
def product_search_tool(
    user: str,
    search_term: Optional[str] = None,
    category_id: Optional[int] = None,
    max_price: Optional[float] = None,
    min_price: Optional[float] = None,
    in_stock_only: bool = False,
    limit: int = 10
) -> dict:
    """Search for products with advanced filtering options."""
    try:
        query = Q(user=user)
        
        if search_term:
            query &= (
                Q(name__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(category__name__icontains=search_term)
            )
        
        if category_id:
            query &= Q(category__id=category_id)
        if min_price:
            query &= Q(price__gte=min_price)
        if max_price:
            query &= Q(price__lte=max_price)
        if in_stock_only:
            query &= Q(stock__gt=0)
            
        products = Product.objects.filter(query).select_related('category')[:limit]
        
        return {
            "products": [{
                "id": p.id,
                "name": p.name,
                "price": float(p.price),
                "stock": p.stock,
                "category": p.category.name if p.category else None
            } for p in products],
            "meta": {
                "count": len(products),
                "user": user
            }
        }
    except Exception as e:
        logger.error(f"Product search failed: {e}")
        return {"error": str(e)}

