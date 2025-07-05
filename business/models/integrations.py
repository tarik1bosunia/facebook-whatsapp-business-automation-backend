from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PlatformIntegration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    platform_id = models.CharField(null=True, blank=True) # Facebook Page ID or WhatsApp Number ID
    access_token = models.CharField(max_length=1000,null=True, blank=True)
    verify_token = models.CharField(max_length=100, null=True, blank=True)
    

    is_connected = models.BooleanField(default=True)
    
    # permissions
    is_send_auto_reply = models.BooleanField(default=True)
    is_send_notification = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True 


class FacebookIntegration(PlatformIntegration):
    class Meta:
        verbose_name = "Facebook Integration"
        verbose_name_plural = "Facebook Integrations"

    def __str__(self):
        return f"Facebook Page: {self.platform_id} (User: {self.user.email})"



class WhatsAppIntegration(PlatformIntegration):
    class Meta:
        verbose_name = "WhatsApp Integration"
        verbose_name_plural = "WhatsApp Integrations"

    def __str__(self):
        return f"WhatsApp Business: {self.platform_id} (User: {self.user.email})"