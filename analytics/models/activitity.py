from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


from django.db import models
from django.utils.translation import gettext_lazy as _

class ActivityType(models.TextChoices):
    CONVERSATION = 'conversation', _('Conversation')
    ORDER = 'order', _('Order')
    FAQ = 'faq', _('FAQ Update')


class SourceType(models.TextChoices):
    FACEBOOK = 'Facebook', _('Facebook')
    WHATSAPP = 'WhatsApp', _('WhatsApp')



class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    type = models.CharField(max_length=20, choices=ActivityType.choices)
    title = models.CharField(max_length=255)
    description = models.TextField()
    source = models.CharField(max_length=20, choices=SourceType.choices, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Activities'
    
    def __str__(self):
        return self.title
    
    @property
    def time_ago(self):
        now = timezone.now()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"