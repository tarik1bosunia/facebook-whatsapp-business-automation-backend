from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Promotion(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="promotions"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.title

    def is_current(self):
        """Check if promotion is currently valid."""
        now = timezone.now()
        return self.is_active and (
            (not self.start_date or self.start_date <= now)
            and (not self.end_date or self.end_date >= now)
        )
