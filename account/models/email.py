from django.db import models

from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
UserModel = get_user_model()

class PendingEmailChange(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pending_email_change'
    )
    new_email = models.EmailField() 
    token = models.CharField(max_length=64, unique=True,)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pending Email Change"
        verbose_name_plural = "Pending Email Changes"
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]

    def clean(self):
        # Validate that new_email isn't already in use by another user
        if UserModel.objects.filter(email=self.new_email).exists():
            raise ValidationError({'new_email': 'This email is already in use by another account'})

    def save(self, *args, **kwargs):
        self.full_clean()  # Runs clean() validation
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def create_for_user(cls, user, new_email, expiration_hours=24):
        """Helper method to create a new pending email change"""
        return cls.objects.create(
            user=user,
            new_email=new_email,
            token=get_random_string(64),
            expires_at=timezone.now() + timezone.timedelta(hours=expiration_hours)
        )

    def __str__(self):
        return f"Pending change for {self.user.email} → {self.new_email}"