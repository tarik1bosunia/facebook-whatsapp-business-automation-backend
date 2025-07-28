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
    # PROVIDER_CHOICES = [
    #     ('GOOGLE', 'Google'),
    #     ('OPENAI', 'OpenAI'),
    #     ('ANTHROPIC', 'Anthropic'),
    #     ('CUSTOM', 'Custom'),
    # ]
    code = models.CharField(max_length=100, unique=True, help_text="Identifier used in APIs, e.g., 'gemini-2.0-flash'")
    name = models.CharField(max_length=100, help_text="Human-readable name, e.g., 'Gemini 2.0 Flash'")
    is_custom = models.BooleanField(default=False) # possibly remove in future and add provider
    # provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
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

    # Token counters
    total_input_tokens = models.PositiveBigIntegerField(
        default=0,
        help_text="Lifetime count of input tokens used"
    )
    total_output_tokens = models.PositiveBigIntegerField(
        default=0,
        help_text="Lifetime count of output tokens generated"
    )
    total_tokens = models.PositiveBigIntegerField(
        default=0,
        help_text="Lifetime total tokens used"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AI Config for {self.user.get_full_name()}"
    

    def update_token_counts(self, usage_metadata: dict):
        """
        Atomically update token counts based on API response metadata.
        
        Args:
            usage_metadata (dict): Dictionary containing:
                - input_tokens (int)
                - output_tokens (int)
                - total_tokens (int)
        """
        if not usage_metadata:
            return

        input_tokens = usage_metadata.get('input_tokens', 0)
        output_tokens = usage_metadata.get('output_tokens', 0)
        total_tokens = usage_metadata.get('total_tokens', 0) or (input_tokens + output_tokens)

        AIConfiguration.objects.filter(pk=self.pk).update(
            total_input_tokens=models.F('total_input_tokens') + input_tokens,
            total_output_tokens=models.F('total_output_tokens') + output_tokens,
            total_tokens=models.F('total_tokens') + total_tokens,
        )
        self.refresh_from_db()

    def get_token_usage_summary(self) -> dict:
        """
        Return comprehensive token usage statistics.
        
        Returns:
            dict: {
                'input_tokens': int,
                'output_tokens': int,
                'total_tokens': int,
            }
        """
        return {
            'input_tokens': self.total_input_tokens,
            'output_tokens': self.total_output_tokens,
            'total_tokens': self.total_tokens,
        }
    