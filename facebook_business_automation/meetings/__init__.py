# facebook_business_automation/settings/__init__.py
import os

DJANGO_ENV = os.environ.get("DJANGO_ENV", "development")

if DJANGO_ENV == "production":
    from .prod import *
else:
    from .dev import *