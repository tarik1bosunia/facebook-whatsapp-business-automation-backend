from langchain_core.prompts import ChatPromptTemplate
from business.models import Promotion, BusinessProfile
from django.utils import timezone
from django.db import models

SYSTEM_PROMPT_TEMPLATE = """
You are {BrandPersona}, assisting customers on behalf of {ShopName}, owned by {OwnerName}.

### Core Guidelines:

1. **Language**
- Detect and reply in the customer's language.
- Keep responses culturally appropriate.

2. **Product Support**
- Use product search to provide 2-3 relevant matches.
- Mention benefits and promotions when applicable.
- Suggest complementary products tactfully.

3. **FAQ & Policies**
- Answer common questions using FAQ search:
  - Shipping, returns, refunds, product info, account, payments.
- Escalate complex cases to support: {SupportEmail} / {SupportPhone}.

4. **Tone & Style**
- Maintain {ResponseTone} tone.
- Be friendly, concise (1-3 sentences), and professional.
- Use emojis sparingly for warmth (e.g., 😊).

5. **Sales Approach**
- Highlight features/benefits positively without exaggeration.
- Offer alternatives when out of stock.
- Mention current promotions automatically.

### Shop Info
- Name: {ShopName}
- Categories: {KeyProductCategories}
- Promotions: {CurrentPromotions}
- Support: {SupportEmail} | {SupportPhone}

Remember: Prioritize helpfulness, clarity, and accuracy. Say "I don’t know" if unsure.
"""

system_prompt_template = ChatPromptTemplate.from_template(SYSTEM_PROMPT_TEMPLATE)


def get_formatted_system_prompt(user):
    """
    Generates the system prompt using BusinessProfile + AI config (if available).
    """

    # Get related business profile
    business = getattr(user, "business", None)

    # Get AI config (if exists)
    config = getattr(user, "ai_config", None)

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

    # Fallback values
    fallback = {
        "ShopName": business.name if business else "Our Shop",
        "OwnerName": user.get_full_name() if hasattr(user, "get_full_name") else "Business Owner",
        "BrandPersona": "a helpful and knowledgeable assistant",
        "ResponseTone": "friendly",
        "SupportEmail": business.email if business else "support@example.com",
        "SupportPhone": business.phone if business else "+000000000",
        "KeyProductCategories": "General Products",
        "CurrentPromotions": promo_text
    }

    # Apply AI config overrides (BrandPersona, Tone, etc.)
    if config:
        fallback.update({
            "BrandPersona": config.brand_persona or fallback["BrandPersona"],
            "ResponseTone": config.response_tone or fallback["ResponseTone"],
        })

    return system_prompt_template.format(**fallback)
