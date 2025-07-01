from django.utils.translation import gettext_lazy as _
from django.db import models


class SENDER_CHOICES(models.TextChoices):
    CUSTOMER = 'customer', _('Customer')
    BUSINESS = 'business', _('Business')
    AI = 'ai', _('AI')


class PLATFORM(models.TextChoices):
    FACEBOOK = 'facebook', _('Facebook')
    WHATSAPP = 'whatsapp', _('WhatsApp')
    INSTAGRAM = 'instagram', _('Instagram')
    TWITTER = 'twitter', _('Twitter')
