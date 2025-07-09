from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
User = get_user_model()


class PlatformIntegration(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name="%(class)s_integration"
    )

    platform_id = models.CharField(
        max_length=255,
        null=True, 
        blank=True,
        verbose_name=_("Platform ID"),
        help_text=_("Facebook Page ID or WhatsApp Number ID")
    ) # Facebook Page ID or WhatsApp Number ID
    
    access_token = models.CharField(
        max_length=1000,
        null=True, 
        blank=True,
        verbose_name=_("Access Token"),
        help_text=_("OAuth token for platform API access")
    )
    verify_token = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name=_("Verify Token"),
        help_text=_("Token for webhook verification")
    )
    

    is_connected = models.BooleanField(
        default=True,
        verbose_name=_("Is Connected"),
        help_text=_("Whether the integration is active")
    )
    
    # permissions
    is_send_auto_reply = models.BooleanField(
        default=True,
        verbose_name=_("Auto Replies Enabled"),
        help_text=_("Enable automatic responses to messages")
    )

    is_send_notification = models.BooleanField(
        default=True,
        verbose_name=_("Notifications Enabled"),
        help_text=_("Enable notifications for new messages")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True 

    def clean(self):
        """Validate that required fields are present when connected"""
        if self.is_connected:
            if not self.platform_id:
                raise ValidationError(_("Platform ID is required when integration is active"))
            if not self.access_token:
                raise ValidationError(_("Access token is required when integration is active"))
            if not self.verify_token:
                raise ValidationError(_("Verify token is required when integration is active"))

        super().clean()

    def __str__(self):
        return f"{self._meta.verbose_name}: {self.platform_id or 'Not Configured'} (User: {self.user.email})"



class FacebookIntegration(PlatformIntegration):
    class Meta:
        verbose_name = _("Facebook Integration")
        verbose_name_plural = _("Facebook Integrations")


class WhatsAppIntegration(PlatformIntegration):
    class Meta:
        verbose_name = _("WhatsApp Integration")
        verbose_name_plural = _("WhatsApp Integrations")