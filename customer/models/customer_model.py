from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from django.contrib.auth import get_user_model
User = get_user_model()

class Customer(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        INACTIVE = 'inactive', _('Inactive')
            

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customers",)    

    name = models.CharField(
        max_length=100,
        verbose_name=_('Name'),
        help_text=_("Customer's full name")
    )
    phone = PhoneNumberField(
        blank=True,
        null=True,
        verbose_name=_('Phone Number'),
        help_text=_("Customer's contact number (e.g., +12125552368)")
    )
    
    # --- Address Fields ---
    city = models.CharField(
        max_length=100,
        verbose_name=_('City'),
        help_text=_("Customer's city")
    )
    police_station = models.CharField(
        max_length=255,
        verbose_name=_('Police Station'),
        help_text=_("Nearest police station for address reference")
    )
    area = models.CharField(
        max_length=255,
        null=True,
        blank=True, # Area is optional
        verbose_name=_('Area/Street Address'),
        help_text=_("Specific area or street address")
    )
    # --- End of Address Fields ---
    
    orders_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Orders Count'),
        help_text=_("Total number of orders placed by this customer")
    )
    total_spent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Total Spent'),
        help_text=_("Total amount spent by this customer")
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_('Status'),
        help_text=_("Customer account status")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.name

    def update_stats(self):
        """Update order count and total spent based on related orders"""
        stats = self.orders.aggregate(
            count=models.Count('id'),
            total=Sum('total')
        )
        self.orders_count = stats['count'] or 0
        self.total_spent = stats['total'] or 0
        self.save(update_fields=['orders_count', 'total_spent'])
        
        
    def get_platforms(self):
        """Return list of platform codes linked to this customer"""
        return list(self.social_media_users.values_list('platform', flat=True).distinct())
    
    def platform_status(self):
        """Return readable platform status"""
        platforms = self.get_platforms()
        if not platforms:
            return "Unknown"
        if len(platforms) > 1:
            return "Both"
        return platforms[0].capitalize()    