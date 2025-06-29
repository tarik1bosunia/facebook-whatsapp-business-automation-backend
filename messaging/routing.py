from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/', consumers.ChatAsyncJsonWebsocketConsumer.as_asgi()),
    # path('ws/chat/<uuid:conversation_id>/',
    #     consumers.ChatConsumer.as_asgi(),
    #     name='chat_ws'
    # ),
    # path(
    #     'ws/notifications/',
    #     consumers.NotificationConsumer.as_asgi(),
    #     name='notification_ws'
    # ),
]
