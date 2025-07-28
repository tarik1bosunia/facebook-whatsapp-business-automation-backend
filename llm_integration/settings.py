# settings.py
# Add these to your settings

# Gemini Configuration
# GEMINI_API_KEY = env('GEMINI_API_KEY', default='your-api-key-here')

# # Cache configuration (using Redis recommended)
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': env('REDIS_URL', default='redis://localhost:6379/1'),
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         },
#         'KEY_PREFIX': 'llm_support'
#     }
# }

# # For vector search (optional)
# INSTALLED_APPS += ['pgvector.django']