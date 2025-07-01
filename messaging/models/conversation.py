from django.db import models
from messaging.models.user import SocialMediaUser
from django.contrib.auth import get_user_model
from messaging.enums import SENDER_CHOICES


User = get_user_model()


class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations")
    socialuser = models.ForeignKey(SocialMediaUser, on_delete=models.CASCADE, related_name='conversations')
    auto_reply = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def last_message(self):
        return self.messages.order_by('-created_at').first()

    def unread_count(self):
        return self.messages.filter(sender=SENDER_CHOICES.CUSTOMER, is_read=False).count()

    def __str__(self):
        return f"Conversation with {self.user.get_full_name()} {self.socialuser.name} ({self.socialuser.social_media_id})"
