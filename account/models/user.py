from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from ..enums import Roles

# TODO: set up password length at least 8

class AuthProvider(models.TextChoices):
    EMAIL = 'email', _('Email')
    GOOGLE = 'google', _('Google')
    GITHUB = 'github', _('GitHub')
    FACEBOOK = 'facebook',_('Facebook')

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    # Personal Info
    email = models.EmailField(
        unique=True,
        verbose_name="Email Address", 
        max_length=255, 
        error_messages={
            'unique': "A user with that email already exists.",
        }
    )
    first_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="First Name")
    last_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="Last Name")
    
     # Status Fields
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Designates whether this user should be treated as active."
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Staff Status",
        help_text="Designates whether the user can log into this admin site."
    )
    is_admin = models.BooleanField(
        default=False,
        verbose_name="Admin Status",
        help_text="Designates whether the user has all permissions without explicitly assigning them."
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    last_password_change = models.DateTimeField(null=True, blank=True, verbose_name="Last Password Change", db_index=True)

    # Authentication
    auth_provider = models.CharField(
        max_length=50,
        choices=AuthProvider.choices,
        default=AuthProvider.EMAIL,
        verbose_name="Authentication Provider"
    )
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name="Email Verified",
        help_text="Designates whether this user's email has been verified."
    )

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.BUSINESSMAN)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']

    def __str__(self):
        return self.email
    

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = " ".join([name for name in [self.first_name, self.last_name] if name])
        return full_name.strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def has_perm(self, perm, obj=None):
        """
        Return True if the user has the specified permission.
        Simplest possible answer: Yes, if admin.
        """
        return self.is_admin
    
    def has_module_perms(self, app_label):
        """
        Return True if the user has permissions to view the app `app_label`.
        """
        return True