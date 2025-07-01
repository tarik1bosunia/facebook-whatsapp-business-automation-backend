from django.urls import path
from .views import ConversationAnalyticsView

urlpatterns = [
    path('api/analytics/conversations/', ConversationAnalyticsView.as_view(), name='conversation-analytics'),

]