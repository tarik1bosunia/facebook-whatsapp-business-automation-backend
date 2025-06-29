from django.db import models

from messaging.models.user import SocialMediaUser


class Conversation(models.Model):
    socialuser = models.ForeignKey(SocialMediaUser, on_delete=models.CASCADE, related_name='conversations')
    auto_reply = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def last_message(self):
        return self.messages.order_by('-created_at').first()

    def unread_count(self):
        return self.messages.filter(sender='customer', is_read=False).count()

    def __str__(self):
        return f"Conversation with {self.socialuser.name} ({self.socialuser.social_media_id})"