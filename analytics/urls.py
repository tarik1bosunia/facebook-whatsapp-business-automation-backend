from django.urls import path

from .views import ConversationAnalyticsView, ActivityListAPIView

urlpatterns = [
    path('activities/', ActivityListAPIView.as_view(), name='activity-list'),
    path('analytics/conversations/', ConversationAnalyticsView.as_view(), name='conversation-analytics'),

]