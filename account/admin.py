from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff',
        'is_superuser', 'auth_provider', 'is_email_verified', 'created_at'
    )
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'auth_provider')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'last_password_change')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name')}),
        (_('Authentication'), {'fields': ('auth_provider', 'is_email_verified')}),
        (_('Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Timestamps'), {'fields': ('last_login', 'last_password_change', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'password1', 'password2',
                'role', 'auth_provider', 'is_email_verified',
                'is_active', 'is_staff', 'is_superuser'
            ),
        }),
    )

