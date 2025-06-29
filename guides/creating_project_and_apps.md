```sh
django-admin startproject facebook_business_automation
python manage.py startapp facebook
python manage.py startapp chatgpt
```

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'facebook',
    'chatgpt',
]
```