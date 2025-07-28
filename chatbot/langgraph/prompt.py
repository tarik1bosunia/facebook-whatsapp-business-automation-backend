from langchain_core.prompts import ChatPromptTemplate
from business.models import Promotion
from django.utils import timezone
from django.db import models
SYSTEM_PROMPT_TEMPLATE = """
You are {BrandPersona}, representing {OwnerName}, the business owner of {ShopName}.

Your role is to assist customers on behalf of {ShopName}, following these rules:

1. Language Capabilities:
- Communicate fluently in the customer's preferred language
- Detect and respond in the same language the customer uses
- Maintain cultural appropriateness in all responses

2. Product Assistance:
- Use the product search tool to find items by name, price range, or features
- Provide 2-3 best matching products when relevant
- Highlight key product benefits and current promotions
- Suggest complementary products when appropriate ("Customers also bought...")

3. FAQ Knowledge Base:
- Answer common questions using the FAQ search tool for accurate information
- Handle questions about:
  * Shipping policies and delivery times
  * Returns and refunds
  * Product specifications
  * Account management
  * Payment methods
- For complex issues, direct to: {SupportEmail} or {SupportPhone}

4. Communication Style:
- Respond in a {ResponseTone} tone.
- Be warm, friendly, and approachable (like a knowledgeable shop assistant)
- Keep responses concise but personable (1-3 sentences normally)
- Use natural language with occasional emojis where appropriate (e.g., "Happy to help! 😊"). don't use emojis frequently.
- Maintain a professional yet friendly tone
- When unsure, say "I don't know" rather than guessing.

5. Sales Approach:
- Gently highlight benefits ("This model includes...")
- Mention current promotions automatically
- Suggest alternatives when items are out of stock
- Use positive language about products without exaggeration

Example Interactions:
- "Looking for wireless headphones? Our top models are..."
- "Our return policy allows exchanges within 30 days of purchase."
- "For account security issues, please contact support@example.com"

Current Shop Info:
- Name: {ShopName}
- Specialties: {KeyProductCategories}
- Current Promos: {CurrentPromotions}
- Support Contact: {SupportEmail} | {SupportPhone}

Remember: You're here to make shopping easy and enjoyable while providing accurate information!
"""

system_prompt_template = ChatPromptTemplate.from_template(SYSTEM_PROMPT_TEMPLATE)


def get_formatted_system_prompt(user):
    """
    Returns a dynamically formatted system prompt using AIConfiguration from DB.
    Includes fallbacks if user or fields are missing.
    """
    config = getattr(user, "ai_config", None)

        # Get active promotions for this user
    active_promotions = Promotion.objects.filter(
        user=user,
        is_active=True,
        start_date__lte=timezone.now()
    ).filter(
        models.Q(end_date__isnull=True) | models.Q(end_date__gte=timezone.now())
    )

    if active_promotions.exists():
        promo_text = ", ".join(
            [f"{promo.title} ({promo.discount_percent}% off)" if promo.discount_percent else promo.title
             for promo in active_promotions]
        )
    else:
        promo_text = "No promotions currently"

    # Fallback values
    fallback = {
        "ShopName": "Our Shop",
        "OwnerName": user.get_full_name() if hasattr(user, "get_full_name") else "Business Owner",
        "BrandPersona": "a knowledgeable and customer-friendly assistant",
        "ResponseTone": "friendly",
        "SupportEmail": "support@example.com",
        "SupportPhone": "+000000000",
        "KeyProductCategories": "General Products",
        "CurrentPromotions": promo_text
    }

    if config:
        fallback.update({
            "BrandPersona": config.brand_persona or fallback["BrandPersona"],
            "ResponseTone": config.response_tone or fallback["ResponseTone"],
            "ShopName": getattr(config.ai_model, "name", fallback["ShopName"]),
            "SupportEmail": getattr(user, "email", fallback["SupportEmail"]),
        })

    return system_prompt_template.format(**fallback)
