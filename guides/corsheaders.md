# [corsheaders](https://pypi.org/project/django-cors-headers/)

## install
```sh
pip install django-cors-headers
```

### in settings.py add it to your installed apps:
```python 
INSTALLED_APPS = [
    ...,
    "corsheaders",
    ...,
]
```
### You will also need to add a middleware class to listen in on responses:
```python
MIDDLEWARE = [
    ...,
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    ...,
]
```

### CORS settings
```python
CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://sub.example.com",
    "http://localhost:8080",
    "http://127.0.0.1:9000",
]
```