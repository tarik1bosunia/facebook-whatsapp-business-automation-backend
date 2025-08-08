# Fixing the Product Search Tool for General Queries

This document explains an issue with the `product_search_tool` when handling general user queries like "what do you have in your shop?" and provides solutions to fix it.

## 1. The Problem

When a user asks a general question about products without specifying any criteria, the AI returns a generic error.

- **User Query:** `tomar dokane ki ki ache` (Bengali for "What do you have in your shop?")
- **AI Response:** `An error occurred while processing your request.`

This happens because the underlying `product_search_tool` is designed for specific, filtered searches and cannot handle general, open-ended queries.

## 2. Root Cause Analysis

The error originates from the validation logic within the tool's input schema. The `InputSchema` in [`chatbot/langgraph/tools/product_search_tool.py`](chatbot/langgraph/tools/product_search_tool.py) includes a validator that requires at least one search filter (`name`, `category`, etc.) to be provided.

A general query like "what do you have?" contains no specific keywords, so the LLM calls the tool with no arguments. This triggers the validator, raises a `ValueError`, and results in the unhelpful error message.

## 3. The Solution: Intelligent Default Behavior

Simply removing the validation and returning a random list of all products is not ideal. A better solution is to make the tool more intelligent. When no filters are specified, it should return a curated list of products that are most likely to be of interest, such as the **newest items**.

This involves two main changes:
1.  Removing the restrictive validation.
2.  Adding logic to the tool to fetch the latest products when no filters are applied.

### Step 1: Remove the `check_at_least_one_filter` Validator

First, remove or comment out the `model_validator` in the `InputSchema` to allow the tool to be called without parameters.

```python
# chatbot/langgraph/tools/product_search_tool.py:49-61

# Delete or comment out this entire method
# @model_validator(mode='after')
# def check_at_least_one_filter(self):
#     if not any([...]):
#         raise ValueError("At least one search filter must be provided.")
#     return self
```

### Step 2: Implement Intelligent Fetching Logic

Next, modify the `_search_products_raw` method. The goal is to check if any search filters were provided.
- If **no filters** are present, it should return the most recently added products.
- If **filters are present**, it should perform the search as before.

The [`Product` model](business/models/product.py:6) is already set up to order products by creation date by default (`ordering = ['-created_at']`), so we just need to make sure we don't override that ordering for general queries.

Here is the recommended implementation for the `_search_products_raw` method:

```python
# chatbot/langgraph/tools/product_search_tool.py:82

def _search_products_raw(self, **kwargs) -> List[ProductSearchResult]:
    """
    Handles the product search and returns Pydantic models.
    For general queries, it returns the newest products.
    """
    queryset = Product.objects.select_related('category').filter(user=self._user)
    
    # --- Start of new logic ---
    filters_applied = any([
        kwargs.get('name'),
        kwargs.get('category'),
        kwargs.get('min_price') is not None,
        kwargs.get('max_price') is not None,
        kwargs.get('in_stock') is not None
    ])
    # --- End of new logic ---

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
    
    # --- Modified result fetching ---
    if not filters_applied:
        # For general queries, use the default ordering ('-created_at') to get the newest products.
        results = list(queryset[:limit])
    else:
        # For specific searches, order by name for predictable results.
        results = list(queryset.order_by('name')[:limit])
    # --- End of modified logic ---
            
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
```

### Step 3: Update the Tool's Description

Finally, update the tool's description to inform the LLM about this new capability.

```python
# chatbot/langgraph/tools/product_search_tool.py:25

description: str = (
    "Searches the product catalog. "
    "Use this tool to find product details by name, category, and price range. "
    "If no filters are provided, it will return a list of the newest products. " # <-- Updated line
    "You can also filter for products that are currently in stock. "
    "This tool's output is structured, making it easy to use for subsequent actions. "
    "For product technical questions, use the product_faq_search_tool instead."
)
```

## 4. Future Improvements: Promotions and Popularity

This solution provides a solid baseline. For even better results, you could consider these enhancements:

- **Featured Products:** Create a `is_featured` boolean field on the `Product` model to allow manual curation of products to show for general queries.
- **Promotions:** The current [`Promotion` model](business/models/promotions.py:7) is not linked to the `Product` model. To feature items on sale, you would need to establish a relationship (e.g., a `ManyToManyField`) between them.
- **Popularity:** Add a counter field to the `Product` model to track views or sales, allowing you to showcase best-selling items.

By implementing the changes in this guide, the tool will handle general queries gracefully and provide more relevant, helpful answers to users.