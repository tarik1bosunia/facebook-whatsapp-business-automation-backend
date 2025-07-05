# Handling Multiple Facebook Pages for a Single Business User

## Problem Identification
The current `OneToOneField` relationship between `User` and `FacebookIntegration` creates inconsistency when a businessman manages multiple Facebook Pages. The model needs restructuring to support one-to-many relationships.

## Solution: One-to-Many Relationship

### Updated Models

```python
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class PlatformIntegration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Changed to ForeignKey
    platform_id = models.CharField(max_length=50, unique=True)
    access_token = models.TextField()
    is_connected = models.BooleanField(default=True)
    
    # permissions
    is_send_auto_reply = models.BooleanField(default=True)
    is_send_notification = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        unique_together = ('user', 'platform_id')

class FacebookIntegration(PlatformIntegration):
    page_name = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = "Facebook Integration"
        verbose_name_plural = "Facebook Integrations"

    def __str__(self):
        return f"{self.page_name} (ID: {self.platform_id})"

class WhatsAppIntegration(PlatformIntegration):
    business_name = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = "WhatsApp Integration"
        verbose_name_plural = "WhatsApp Integrations"



# Facebook Integration Update

## 🔑 Key Changes

- 🔄 Changed `OneToOneField` → `ForeignKey` to support **multiple pages per user**
- 🔐 Added `unique=True` to `platform_id` for page identity
- 🤝 Introduced `unique_together` constraint (`user`, `platform_id`) to prevent duplicates
- 🏷️ Added `page_name` and related fields for better clarity
- 🚫 Made `access_token` field **non-nullable**

---

## 🔔 Webhook Handling

```python
def handle_facebook_webhook(payload):
    page_id = payload["entry"][0]["id"]
    try:
        integration = FacebookIntegration.objects.get(platform_id=page_id)
        business_user = integration.user
        # Process message...
    except FacebookIntegration.DoesNotExist:
        raise Exception("Facebook Page not connected to any account")



# 🔧 Managing Multiple Pages
## ✅ Connecting Pages

```python
# Connect first page
FacebookIntegration.objects.create(
    user=request.user,
    platform_id="PAGE_ID_1",
    access_token="TOKEN_1",
    page_name="Main Business Page"
)

# Connect second page
FacebookIntegration.objects.create(
    user=request.user,
    platform_id="PAGE_ID_2",
    access_token="TOKEN_2",
    page_name="Secondary Page"
)
```

# 📋 Retrieving User's Pages
```
user_facebook_pages = FacebookIntegration.objects.filter(user=request.user)
for page in user_facebook_pages:
    print(f"Page: {page.page_name}, ID: {page.platform_id}")
```

# 🎯 Benefits
✅ One user can manage multiple Facebook pages

✅ Each page maintains separate settings

✅ Messages clearly attributed to the correct page

✅ Duplicate connections prevented by constraints


