from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

# TODO: phone and email need to make it unique so that more than 1 customer can not use same email and phone

class Customer(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        INACTIVE = 'inactive', _('Inactive')

    name = models.CharField(
        max_length=100,
        verbose_name=_('Name'),
        help_text=_("Customer's full name")
    )
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_('Email'),
        help_text=_("Customer's email address")
    )
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_('Phone Number'),
        help_text=_("Customer's contact number")
    )
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
            models.Index(fields=['email']),
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