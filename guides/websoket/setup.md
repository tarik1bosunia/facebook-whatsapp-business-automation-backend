# WebSocket support to Django [channels](https://channels.readthedocs.io/en/latest/installation.html)
```sh
pip install -U 'channels[daphne]'
pip install channels-redis
```
### in settings.py
```python
"daphne", in instllaed apps
ASGI_APPLICATION = "your_project_name.asgi.application"

# Example Redis config for channel layer
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```
### In-Memory Channel Layer for local developmet(Do Not Use In Production)
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
```

### in project_name/asgi.py
```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import your_app.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            your_app.routing.websocket_urlpatterns
        )
    ),
})
```