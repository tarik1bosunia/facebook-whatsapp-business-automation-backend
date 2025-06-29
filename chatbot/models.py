from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ModelChoices(models.TextChoices):
    GEMINI_PRO = 'gemini-2.0-flash', 'Gemini 2.0 Flash'
    GEMINI_ULTRA = 'gemini-ultra', 'Gemini Ultra'
    CUSTOM = 'custom', 'Custom Model'


class ToneChoices(models.TextChoices):
    FRIENDLY = 'friendly', 'Friendly and Casual'
    PROFESSIONAL = 'professional', 'Professional'
    FORMAL = 'formal', 'Formal'
    HELPFUL = 'helpful', 'Helpful and Informative'

DEFAULT_BRAND_PERSONA = """Represent our brand as a knowledgeable, professional, and customer-focused organization. Respond in a friendly yet polished tone that balances expertise with approachability.

Key guidelines:
1. Be concise but thorough
2. Maintain professional yet warm tone
3. Focus on accurate, helpful information
4. Protect user privacy and data security
5. Use clear, accessible language

Company values:
- Commitment to excellence
- Customer-first approach
- Ethical business practices"""

class AIModel(models.Model):
    code = models.CharField(max_length=100, unique=True, help_text="Identifier used in APIs, e.g., 'gemini-2.0-flash'")
    name = models.CharField(max_length=100, help_text="Human-readable name, e.g., 'Gemini 2.0 Flash'")
    is_custom = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name



class AIConfiguration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ai_config')
    # ai_model = models.CharField(max_length=20, choices=ModelChoices.choices, default=ModelChoices.GEMINI_PRO)
    ai_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='configurations')
    api_key = models.CharField(max_length=255, null=True, blank=True)  # TODO: In production, use Django's cryptography or a secrets manager
    response_tone = models.CharField(max_length=20, choices=ToneChoices.choices, default=ToneChoices.FRIENDLY)
    brand_persona = models.TextField(default=DEFAULT_BRAND_PERSONA)

    # Behavior Settings
    auto_respond = models.BooleanField(default=True)
    generate_suggestions = models.BooleanField(default=True)
    human_handoff = models.BooleanField(default=True)
    learn_from_history = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AI Config for {self.user.get_full_name()}"
    