# /app/chatbot/langgraph/prompt.py

from langchain_core.prompts import ChatPromptTemplate
from business.models import Promotion, BusinessProfile, ProductCategory
from django.utils import timezone
from django.db import models

SYSTEM_PROMPT_TEMPLATE = """
You are {BrandPersona}, assisting customers on behalf of {ShopName}, owned by {OwnerName}.

### Core Guidelines:

1. **Language**
- Detect and reply in the customer's language.
- Keep responses culturally appropriate.

2. **Product & Service Support**
- Use product search to provide 2-3 relevant matches.
- Mention benefits and promotions when applicable.
- **Currency**: All prices must be in BDT TK.
- Suggest complementary products tactfully.

3. **FAQ & Policies**
- Answer common questions using FAQ search:
  - Shipping, returns, refunds, product info, account, payments.
- Escalate complex cases to support: {SupportEmail} / {SupportPhone}.

4. **Sales & Order Management**
- When a customer is ready to purchase, use the `order_confirmation_tool` to finalize the sale.
- To use the tool, you must gather all required information: order number, customer details (name/ID), total cost, and number of items.
- If a customer's details (name, email, or phone) are not known, first ask for them.
- Do not use this tool for general inquiries; it is for creating confirmed orders only.
- Mention current promotions automatically.

5. **Tone & Style**
- Maintain {ResponseTone} tone.
- Be friendly, concise (1-3 sentences), and professional.
- Use emojis sparingly for warmth (e.g., 😊).

### Shop Info
- Name: {ShopName}
- Categories: {KeyProductCategories}
- Promotions: {CurrentPromotions}
- Support: {SupportEmail} | {SupportPhone}
- Current Date and Time: {CurrentDateTime}

Remember: Prioritize helpfulness, clarity, and accuracy. Say "I don't know" if unsure.
"""

system_prompt_template = ChatPromptTemplate.from_template(SYSTEM_PROMPT_TEMPLATE)


def get_formatted_system_prompt(user):
    """
    Generates the system prompt using user-related data and AI config.
    """
    # Assuming user has an `ai_config` and `business` related objects
    config = getattr(user, "ai_config", None)
    business = getattr(user, "business", None)

    # Active promotions
    active_promotions = Promotion.objects.filter(
        user=user,
        is_active=True,
        start_date__lte=timezone.now()
    ).filter(
        models.Q(end_date__isnull=True) | models.Q(end_date__gte=timezone.now())
    )

    promo_text = ", ".join(
        [f"{promo.title} ({promo.discount_percent}% off)" if promo.discount_percent else promo.title
         for promo in active_promotions]
    ) or "No promotions currently"

    # Fetch key product categories associated with the user
    try:
        categories = ProductCategory.objects.filter(user=user)
        categories_text = ", ".join([cat.name for cat in categories]) or "General Products"
    except (ProductCategory.DoesNotExist, AttributeError):
        categories_text = "General Products"

    # Fallback values for the prompt, derived from user and related models
    context = {
        "ShopName": getattr(business, "name", "Our Shop"),
        "OwnerName": user.get_full_name() or "Business Owner",
        "BrandPersona": getattr(config, "brand_persona", "a helpful and knowledgeable assistant"),
        "ResponseTone": getattr(config, "response_tone", "friendly"),
        "SupportEmail": getattr(business, "email", "support@example.com"),
        "SupportPhone": getattr(business, "phone", "+000000000"),
        "KeyProductCategories": categories_text,
        "CurrentPromotions": promo_text,
        "CurrentDateTime": timezone.now().strftime("%A, %B %d, %Y, %I:%M:%S %p %Z")
    }
    
    return system_prompt_template.format(**context)