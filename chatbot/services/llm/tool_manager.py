

import json
from typing import List, Optional

from langchain.tools import BaseTool, Tool
from chatbot.services.llm.vector_store import PGVectorStore
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from decimal import Decimal
from django.db.models import Q

from business.models import Product
from .tools import product_search_tool, document_search_tool
from langchain_core.tools import BaseTool
import logging
logger = logging.getLogger(__name__)

from langchain_core.tools import tool

class ToolManager:
    """Manages the creation and execution of agent tools"""

    def __init__(self, user, vector_store: Optional[PGVectorStore] = None):
        self.user = user
        self.vector_store = vector_store

    def get_tools(self) -> List[BaseTool]:
        """Get all available tools"""
        tools = [
            self._init_product_tool(),
            self._init_document_tool(),
            # self._create_faq_search_tool(),
            # self._create_business_info_tool()
        ]

        if self.vector_store:
            tools.append(self._create_document_search_tool())

        return tools
    
    def _init_product_tool(self) -> BaseTool:
        """Initialize the product search tool with user context"""
        tool = product_search_tool.bind(user=self.user)
        return Tool(
            name="ProductSearch",
            func=tool.func,
            description=tool.description,
            args_schema=tool.args_schema,
        )
    
    def _init_document_tool(self) -> BaseTool:
        """Initialize the document search tool with vector store context"""
        tool = document_search_tool.bind(vector_store=self.vector_store)
        return Tool(
            name="DocumentSearch",
            func=tool.func,
            description=tool.description,
            args_schema=tool.args_schema,
        )

    def _create_document_search_tool(self) -> BaseTool:
        return Tool(
            name="DocumentSearch",
            func=self._safe_document_search,
            description="Search in stored documents using semantic search"
        )

    def _create_product_search_tool(self) -> BaseTool:
        return Tool(
            name="ProductSearch",
            func=self._safe_product_search,
            description="Search for products"
        )

    def _create_faq_search_tool(self) -> BaseTool:
        return Tool(
            name="FAQSearch",
            func=self._safe_faq_search,
            description="Search knowledge base"
        )

    def _create_business_info_tool(self) -> BaseTool:
        return Tool(
            name="BusinessInfo",
            func=self._safe_business_info,
            description="Get business details"
        )

    def _safe_document_search(self, query: str) -> str:
        """Safe document search with error handling"""
        if not self.vector_store:
            return "Document search is not available"

        try:
            results = self.vector_store.similarity_search(query, k=3)
            return "\n\n".join([doc.page_content for doc in results])
        except Exception as e:
            logger.error(f"Document search failed: {str(e)}")
            return "Document search is currently unavailable"
    def _safe_product_search(user, search_term=None, category_id=None, max_price=None, min_price=None, in_stock_only=False, limit=10):
        """
        Comprehensive product search that handles:
        - Full-text search across name, description
        - Category filtering
        - Price range filtering
        - Stock availability
        - Returns structured data for LLM
        
        Args:
            user: The business owner/user
            search_term: Optional search string
            category_id: Optional category filter
            max_price: Optional maximum price
            min_price: Optional minimum price
            in_stock_only: Only return in-stock items
            limit: Maximum results to return
            
        Returns:
            {
                "products": [list of product dicts],
                "filters": {applied filters},
                "error": null/error_message
            }
        """
        try:
            # Base query - always filter by user
            query = Q(user=user)
            
            # Apply text search if provided
            if search_term and search_term.strip():
                search_term = search_term.strip()
                query &= (
                    Q(name__icontains=search_term) |
                    Q(description__icontains=search_term) |
                    Q(category__name__icontains=search_term)
                )
            
            # Apply category filter if provided
            if category_id:
                query &= Q(category__id=category_id)
                
            # Apply price range filters
            if min_price is not None:
                query &= Q(price__gte=min_price)
            if max_price is not None:
                query &= Q(price__lte=max_price)
                
            # Apply stock filter
            if in_stock_only:
                query &= Q(stock__gt=0)
                
            # Execute query
            products = Product.objects.filter(query).select_related('category')[:limit]
            
            # Prepare results
            product_data = []
            for p in products:
                product_data.append({
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "price": str(p.price),  # Convert Decimal to string
                    "stock": p.stock,
                    "category": {
                        "id": p.category.id if p.category else None,
                        "name": p.category.name if p.category else None
                    },
                    "created_at": p.created_at.isoformat(),
                    "updated_at": p.updated_at.isoformat()
                })
                
            return {
                "products": product_data,
                "filters": {
                    "search_term": search_term,
                    "category_id": category_id,
                    "min_price": min_price,
                    "max_price": max_price,
                    "in_stock_only": in_stock_only
                },
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Product search failed: {str(e)}")
            return {
                "products": [],
                "filters": {},
                "error": str(e)
            }

    def _safe_faq_search(self, query: str) -> str:
        """FAQ search with error handling"""
        try:
            from knowledge_base.models import FAQ
            faqs = FAQ.objects.filter(
                category__user=self.user
            )[:3].values('question', 'answer')
            return json.dumps(list(faqs))
        except Exception as e:
            logger.error(f"FAQ search failed: {str(e)}")
            return json.dumps({"error": "FAQ search unavailable"})

    def _safe_business_info(self, query: str) -> str:
        """Business info with error handling"""
        try:
            from business.models import BusinessProfile
            business = BusinessProfile.objects.get(user=self.user)
            return json.dumps({
                'name': business.name,
                'email': business.email,
                'phone': business.phone
            })
        except Exception as e:
            logger.error(f"Business info failed: {str(e)}")
            return json.dumps({"error": "Business info unavailable"})
        

class DecimalEncoder(DjangoJSONEncoder):
    """Custom JSON encoder that handles Decimal types"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)  # Preserve precision as string
        return super().default(obj)