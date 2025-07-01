from datetime import datetime, timedelta
from django.db.models import Count
from ..models import Conversation, ChatMessage

class AnalyticsService:
    @staticmethod
    def get_conversation_stats(user):
        now = datetime.now()
        current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month = (current_month - timedelta(days=1)).replace(day=1)
        
        # Total conversations count
        total = Conversation.objects.filter(user=user).count()
        
        # Current month conversations
        current_count = Conversation.objects.filter(
            user=user,
            created_at__gte=current_month
        ).count()
        
        # Last month conversations
        last_count = Conversation.objects.filter(
            user=user,
            created_at__gte=last_month,
            created_at__lt=current_month
        ).count()
        
        # Calculate percentage change
        change = 0
        if last_count > 0:
            change = ((current_count - last_count) / last_count) * 100
        
        return {
            'total': total,
            'change': round(abs(change)),
            'trend': 'up' if change >= 0 else 'down'
        }