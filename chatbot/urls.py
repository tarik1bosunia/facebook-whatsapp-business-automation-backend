from django.urls import include, path
from .views import AIConfigurationView, chat_with_ai, ChatMessageAPIView, AIModelViewSet, AdvanceChatAPIView, LangGraphChatAPIView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'ai-models', AIModelViewSet, basename='aimodel')


urlpatterns = [
    path('', include(router.urls)),
    path('api/chat/', chat_with_ai, name='chat-with-ai'),
    path('ai-config/', AIConfigurationView.as_view(), name='ai-configuration'),
    path("auto-response/", ChatMessageAPIView.as_view(), name="auto-response"),
    path("advance-chat/", AdvanceChatAPIView.as_view(), name="advance-chat"),
    path("langgraph-chat/", LangGraphChatAPIView.as_view(), name="langgraph-chat")
]

