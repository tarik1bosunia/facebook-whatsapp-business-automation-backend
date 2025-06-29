from django.db import models


class BaseMessage(models.Model):
    message_id = models.CharField(max_length=255, unique=True)
    sender_id = models.CharField(max_length=255)
    recipient_id = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    content = models.JSONField()
    status = models.CharField(max_length=50)
    platform = models.CharField(max_length=20)

    class Meta:
        abstract = True

    def to_standard_format(self):
        return {
            "id": self.message_id,
            "sender": self.sender_id,
            "platform": self.platform,
            "content": self.content
        }