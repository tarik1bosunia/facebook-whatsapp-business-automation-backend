# How to Create a User with an Unusable Password
## 1. In **UserManager** (when creating users):
```python
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        
        if password:
            user.set_password(password)  # Set password if provided
        else:
            user.set_unusable_password()  # Mark password as unusable
        
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        
        return self.create_user(email, password, **extra_fields)
```
## 2. Manually Setting an Unusable Password (e.g., for OAuth users):
```python
from django.contrib.auth.hashers import make_password, is_password_usable

user = User.objects.get(email="user@example.com")

if not is_password_usable(user.password):
    print("This user has no usable password (likely social login).")
else:
    print("This user has a password.")
```

## 3. Checking if a Password is Unusable:
```python
from django.contrib.auth.hashers import make_password, is_password_usable

user = User.objects.get(email="user@example.com")

if not is_password_usable(user.password):
    print("This user has no usable password (likely social login).")
else:
    print("This user has a password.")
```



# Why Use `set_unusable_password()`?

## 1️⃣ For OAuth/Social Logins:
Users signing in through **Google**, **Github**, or other providers don't need a password in your application.  
Using `set_unusable_password()` lets you create a user account without a password.

## 2️⃣ Security:
It prevents **accidental password authentication** for those accounts.  
This avoids confusion and potential vulnerabilities if someone were to attempt password login for a social account.

## 3️⃣ Django Convention:
The `AbstractBaseUser` model expects **every user to have a password**, even if it's unusable.  
`set_unusable_password()` gracefully handles this by marking the password as unusable instead of `NULL`.

---

# How Django Handles Unusable Passwords Internally:

- `set_unusable_password()` sets `user.password` to **an invalid hash** (not `None`).
- `check_password()` will always return `False` for such users.
- `is_password_usable(user.password)` checks whether the password is usable or not.

---

✅ **This approach lets you maintain a unified User model while keeping password authentication flexible and secure.**
