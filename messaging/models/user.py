from django.db import models

from customer.models import Customer
from django.utils.translation import gettext_lazy as _

class PLATFORM(models.TextChoices):
        FACEBOOK = 'facebook', _('Facebook')
        WHATSAPP = 'whatsapp', _('WhatsApp')
        INSTAGRAM = 'instagram', _('Instagram')
        TWITTER = 'twitter', _('Twitter')


class SocialMediaUser(models.Model):
    name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Name'),
        help_text=_("Name of the social media user")
    )
    social_media_id = models.CharField(
        max_length=50,
        verbose_name=_('Social Media ID'),
        help_text=_("Unique identifier from the social platform")
    )
    avatar_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_('Avatar URL'),
        help_text=_("URL to the socialuser's profile picture")
    )
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM.choices,
        db_index=True,
        verbose_name=_('Platform'),
        help_text=_("Social media platform")
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        related_name='social_media_users',
        null=True,
        blank=True,
        verbose_name=_('Customer'),
        help_text=_("Linked customer account")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )

    class Meta:
        verbose_name = _('Social Media User')
        verbose_name_plural = _('Social Media Users')
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['platform', 'social_media_id']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['platform', 'social_media_id'],
                name='unique_social_media_user'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.platform} - {self.social_media_id})"