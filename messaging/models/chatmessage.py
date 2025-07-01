from django.db import models

from messaging.models.conversation import Conversation
from django.utils.translation import gettext_lazy as _
from messaging.enums import SENDER_CHOICES

class ChatMessage(models.Model):

    DOWNLOAD_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES, default=SENDER_CHOICES.BUSINESS)

    # For text or caption
    message = models.TextField(blank=True, null=True) # for text or caption

    # Media fields
    media_id = models.CharField(max_length=255, blank=True, null=True) # WhatsApp media ID
    media_type = models.CharField(max_length=50, blank=True, null=True)

    # for Messenger:
    messenger_media_url = models.URLField(blank=True, null=True, max_length=1000)  # Temporary CDN URL
    messenger_media_file = models.FileField(upload_to='messenger_images/', blank=True, null=True)

    # Download tracking
    download_status = models.CharField(
        max_length=10,
        choices=DOWNLOAD_STATUS_CHOICES,
        default='completed',
        null=True,
        blank=True
    )

    contacts = models.JSONField(
        blank=True, 
        null=True,
    )  # For contacts message type (stores entire contacts array)

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        snippet = self.message[:50] if self.message else "[No message text]"
        return f"{self.conversation}: {self.sender} - {snippet}"