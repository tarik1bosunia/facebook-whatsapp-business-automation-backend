from langchain_core.tools import BaseTool
from typing import List, Type, Optional
import logging
from pydantic import BaseModel, Field, PrivateAttr, model_validator # ✅ Use model_validator
from django.db.models import Q
from business.models import Product, ProductCategory
from account.models import User

logger = logging.getLogger(__name__)


# Pydantic model for a structured Product result
class ProductSearchResult(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    category: str
    description: str

class ProductSearchTool(BaseTool):
    """Tool that searches for products in the database."""
    
    name: str = "product_search_tool"
    description: str = (
        "Searches the product catalog with multiple filters. "
        "Use this tool to find product details by name, category, and price range. "
        "You can also filter for products that are currently in stock. "
        "This tool's output is structured, making it easy to use for subsequent actions like order confirmation. "
        "For product technical questions, use the product_faq_search_tool instead. "
        "Example usage: `product_search_tool(name='iphone', in_stock=True, max_price=1000)`"
    )

    _user: User = PrivateAttr()

    def __init__(self, user: User, **kwargs):
        super().__init__(**kwargs)
        self._user = user

    class InputSchema(BaseModel):
        name: Optional[str] = Field(None, description="Search for a product by its name.")
        category: Optional[str] = Field(None, description="Filter products by category name.")
        min_price: Optional[float] = Field(None, description="Filter for products with a price greater than or equal to this value.")
        max_price: Optional[float] = Field(None, description="Filter for products with a price less than or equal to this value.")
        in_stock: Optional[bool] = Field(None, description="Set to `True` to filter only for products that are currently in stock.")
        limit: Optional[int] = Field(10, description="Maximum number of results to return.")

        # ✅ Corrected: Using Pydantic V2's model_validator
        @model_validator(mode='after')
        def check_at_least_one_filter(self):
            if not any(
                [
                    self.name,
                    self.category,
                    self.min_price is not None,
                    self.max_price is not None,
                    self.in_stock is not None
                ]
            ):
                raise ValueError("At least one search filter (name, category, price, or stock) must be provided.")
            return self
    
    args_schema: Type[BaseModel] = InputSchema
    
    def _run(self, **kwargs) -> str:
        """
        Searches products based on structured input and returns a formatted string.
        """
        try:
            results = self._search_products_raw(**kwargs)
            if not results:
                return "No products found matching your criteria."
            
            return self._format_results(results)
        except ValueError as e:
            logger.error(f"Product search failed: {str(e)}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"An unexpected error occurred during product search: {str(e)}")
            return "An unexpected error occurred during product search."

    def _search_products_raw(self, **kwargs) -> List[ProductSearchResult]:
        """
        Handles the product search and returns Pydantic models.
        This is the method an agent would use for tool chaining.
        """
        queryset = Product.objects.select_related('category').filter(user=self._user)
        
        if kwargs.get('name'):
            queryset = queryset.filter(Q(name__icontains=kwargs['name']) | Q(description__icontains=kwargs['name']))
        
        if kwargs.get('category'):
            queryset = queryset.filter(category__name__icontains=kwargs['category'])
            
        if kwargs.get('min_price') is not None:
            queryset = queryset.filter(price__gte=kwargs['min_price'])
            
        if kwargs.get('max_price') is not None:
            queryset = queryset.filter(price__lte=kwargs['max_price'])
            
        if kwargs.get('in_stock'):
            queryset = queryset.filter(stock__gt=0)
            
        limit = kwargs.get('limit', 10)
        results = list(queryset.order_by('name')[:limit])
            
        return [
            ProductSearchResult(
                id=p.id,
                name=p.name,
                price=float(p.price),
                stock=p.stock,
                category=p.category.name if p.category else "Uncategorized",
                description=p.description
            ) for p in results
        ]

    def _format_results(self, results: List[ProductSearchResult]) -> str:
        """Format the search results from a list of Pydantic models"""
        formatted_list = [f"Found {len(results)} products matching your criteria:"]
        
        for product in results:
            stock_status = "In Stock" if product.stock > 0 else "Out of Stock"
            formatted_list.append(
                f"\n- Product Name: {product.name}"
                f"\n  Price: ${product.price:.2f}"
                f"\n  Category: {product.category}"
                f"\n  Stock: {product.stock} ({stock_status})"
                f"\n  Description: {product.description[:100]}{'...' if len(product.description) > 100 else ''}"
                f"\n  ID: {product.id}"
            )
        
        return "\n".join(formatted_list)
        
    def _arun(self, *args, **kwargs):
        """Async version not implemented."""
        raise NotImplementedError("Async operation not supported")