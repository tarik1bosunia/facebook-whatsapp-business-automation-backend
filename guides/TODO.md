# TODO
- apply pagination
- apply websocket

# TODO imidiate
- now i am going to login with google
-  I have to handle a issue ... without email verified i can't access user any of the api without sent email verification
- timestamp field may be need to add in ChatMessage model so need to change code according it both frontend and backend
- message_type may be need to add for ChatMessage 
- Currently don't have polls support for whatsapp so I can't implement it.
- only with refresh token can access those route(but is_email_active also need to be true)
- currently sent message implemented by http request , need to convet it into websocket(major task)
- need to work with time in settings.py

# TODO for production
### 1. change channels layer settings in settings.py to 
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```
# add frontend domains in settings.py ALLOWED_HOSTS and ALLOWED_FRONTEND_DOMAINS
```python
ALLOWED_HOSTS = [
    'localhost',
    '4b4f-37-111-227-60.ngrok-free.app', # temporary for testing webhook
    '127.0.0.1',
]

# this is for multiple frontend single backend activation link sent in email , activation link need to fronetned domain
# 
ALLOWED_FRONTEND_DOMAINS = [
    'rateteach.ru.ac.bd',
    'localhost:3000',  # for development
    # add other allowed frontend domains
]
```

# Possible improvements
1. here the code only work for a single page in facebook  & wahtsapp work for single business

