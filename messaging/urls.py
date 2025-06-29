from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, ChatMessageViewSet, send_message, AutoReplyToggleView, SocialMediaUserViewSet, media_proxy

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', ChatMessageViewSet, basename='chatmessage')
router.register(r'social-media-users', SocialMediaUserViewSet, basename='socialmediauser')

from messaging.views.webhooks import messenger_webhook, whatsapp_webhook

urlpatterns = [
    path('', include(router.urls)),
    path('send-message/', send_message, name='send_message'),
    path('conversations/<int:pk>/auto-reply/', AutoReplyToggleView.as_view(), name='conversation-auto-reply'),
    path('webhook/messenger/', messenger_webhook, name='messenger-messaging-webhook'),
    path('webhook/whatsapp/', whatsapp_webhook, name='whatsapp-messaging-webhook'),
    path('media-proxy', media_proxy, name='media_proxy'),
]