from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PlatformIntegration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.TextField(null=True, blank=True)
    is_connected = models.BooleanField(default=True)
    
    # permissions
    is_send_auto_reply = models.BooleanField(default=True)
    is_send_notification = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True 


class FacebookIntegration(PlatformIntegration):
    pass


class WhatsAppIntegration(PlatformIntegration):
    pass
