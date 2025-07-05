import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dc1.settings')

django_asgi_app = get_asgi_application()

from .middlewares import JWTAuthMiddlewareStack
from messaging.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddlewareStack(URLRouter(websocket_urlpatterns))
})