# How to Use django-phonenumber-field

This guide provides a step-by-step walkthrough on how to integrate and use the `django-phonenumber-field` library in your Django project. This library simplifies phone number handling by providing a validated, international-ready model and form field.

## 1. Why Use `django-phonenumber-field`?

Storing phone numbers in a simple `CharField` is prone to errors. Users might enter numbers in various formats (e.g., `(123) 456-7890`, `123-456-7890`, `+11234567890`), and validating them manually is complex.

`django-phonenumber-field` solves this by:

- **Standardizing** phone numbers into the E.164 format (e.g., `+12125552368`).
- **Validating** that the number is plausible for its country code.
- Providing easy integration with models, forms, and serializers.

## 2. Installation

First, you need to install the library and its required dependency, `phonenumbers`.

```bash
pip install django-phonenumber-field[phonenumbers]
```

The `[phonenumbers]` extra ensures that the underlying `phonenumbers` library from Google is also installed.

## 3. Configuration

After installation, add `phonenumber_field` to your `INSTALLED_APPS` in your project's `settings.py` file.

**File:** `facebook_business_automation/settings.py` (or your project's settings file)

```python
# settings.py

INSTALLED_APPS = [
    # ... other apps
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
    'phonenumber_field', # Add this line
]
```

No other configuration is required for basic use.

## 4. Usage in Models

To use it in your models, import `PhoneNumberField` and replace your existing `CharField` for phone numbers.

**File:** [`customer/models/customer_model.py`](customer/models/customer_model.py)

```python
# customer/models/customer_model.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField # 1. Import the field

class Customer(models.Model):
    # ... (name, email, etc.)

    # 2. Replace CharField with PhoneNumberField
    phone = PhoneNumberField(
        blank=True,
        null=True,
        verbose_name=_('Phone Number'),
        help_text=_("Customer's contact number in international format (e.g., +12125552368)")
    )

    # ... (rest of the model)
```

### Database Migrations

After changing the model field, you must create and apply a database migration for the change to take effect.

```bash
python manage.py makemigrations
python manage.py migrate
```

## 5. Usage in Serializers (Django Rest Framework)

If you are using Django Rest Framework, you can also use `PhoneNumberField` in your serializers for automatic validation at the API level.

**File:** `customer/serializers/customer_serializer.py` (example path)

```python
# customer/serializers/customer_serializer.py

from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from ..models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    # The serializer field will automatically validate the phone number format
    phone = PhoneNumberField()

    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'city', 'police_station', 'area']
```

When a user submits data to an API endpoint using this serializer, the `phone` field will be automatically validated. If the number is invalid, the API will return a standard DRF validation error, which is much clearer than the generic error seen previously.

## 6. How It Solves the Validation Problem

By using `PhoneNumberField`, the validation is handled for you.

- When a customer provides a number like `01720198552`, the library can parse it (often requiring a default region setting in `settings.py` if the country code is missing, e.g., `PHONENUMBER_DEFAULT_REGION = 'BD'`).
- It will raise a `ValidationError` with a clear message if the number is impossible (e.g., has too many digits for a given country).
- The number is stored in a standardized format in the database, ensuring data consistency.

This approach is more robust, reliable, and follows best practices for handling international phone numbers.
