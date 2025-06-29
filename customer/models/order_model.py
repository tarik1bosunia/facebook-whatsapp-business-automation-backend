from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _
from .customer_model import Customer

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        SHIPPED = 'shipped', _('Shipped')
        DELIVERED = 'delivered', _('Delivered')
        CANCELLED = 'cancelled', _('Cancelled')

    class PaymentStatus(models.TextChoices):
        PAID = 'paid', _('Paid')
        PENDING = 'pending', _('Pending')
        REFUNDED = 'refunded', _('Refunded')

    class Source(models.TextChoices):
        FACEBOOK = 'facebook', _('Facebook')
        WHATSAPP = 'whatsapp', _('Whatsapp')
        MANUAL = 'manual', _('Manual')


    order_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('Order Number'),
        help_text=_("Unique identifier for the order"),
        validators=[MinLengthValidator(5)]
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('Customer'),
        help_text=_("Customer who placed this order")
    )
    items = models.PositiveIntegerField(
        verbose_name=_('Items Count'),
        help_text=_("Number of items in this order")
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Order Total'),
        help_text=_("Total amount for this order")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_('Order Status'),
        help_text=_("Current status of the order")
    )
    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.MANUAL,
        verbose_name=_('Source'),
        help_text=_("From which source the order is from")
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name=_('Payment Status'),
        help_text=_("Current payment status of the order")
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
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['customer']),
        ]

    def __str__(self):
        return f"{self.order_number} - {self.customer.name}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new or self.has_important_changes():
            self.customer.update_stats()

    def has_important_changes(self):
        """Check if status or payment status has changed"""
        if not self.pk:
            return False

        original = Order.objects.get(pk=self.pk)
        return (
                original.status != self.status or
                original.payment_status != self.payment_status
        )
