from django.db import models
from django.contrib.auth import get_user_model
# from django.core.exceptions import ValidationError, MinValueValidator

User = get_user_model()


class Service(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name="Service Provider"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Service Name"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Detailed Description"
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        # validators=[MinValueValidator(0.01)],
        verbose_name="Starting Price"
    )
    duration_minutes = models.PositiveIntegerField(
        verbose_name="Duration (minutes)",
        help_text="Approximate time needed to complete the service"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active Service"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def clean(self):
    #     if self.base_price <= 0:
    #         raise ValidationError(
    #             {'base_price': "Base price must be positive."})
    #     if self.duration_minutes <= 0:
    #         raise ValidationError(
    #             {'duration_minutes': "Duration must be positive."})
        
    @property
    def hourly_rate(self):
        return (self.base_price / self.duration_minutes) * 60    

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (by {self.user})"
