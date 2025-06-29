from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Customer, Order

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'orders_count', 'total_spent', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('orders_count', 'total_spent', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'phone', 'status')
        }),
        (_('Statistics'), {
            'fields': ('orders_count', 'total_spent')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_active', 'mark_as_inactive']

    def mark_as_active(self, request, queryset):
        queryset.update(status=Customer.Status.ACTIVE)
    mark_as_active.short_description = _("Mark selected customers as active")

    def mark_as_inactive(self, request, queryset):
        queryset.update(status=Customer.Status.INACTIVE)
    mark_as_inactive.short_description = _("Mark selected customers as inactive")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'items', 'total', 'status', 'payment_status', 'source', 'created_at')
    list_filter = ('status', 'payment_status', 'source', 'created_at')
    search_fields = ('order_number', 'customer__name', 'customer__email', 'customer__phone')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('customer',)
    fieldsets = (
        (None, {
            'fields': ('order_number', 'customer', 'items', 'total')
        }),
        (_('Status'), {
            'fields': ('status', 'payment_status', 'source')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_editable = ('status', 'payment_status')
    actions = ['mark_as_paid', 'mark_as_refunded']

    def mark_as_paid(self, request, queryset):
        queryset.update(payment_status=Order.PaymentStatus.PAID)
    mark_as_paid.short_description = _("Mark selected orders as paid")

    def mark_as_refunded(self, request, queryset):
        queryset.update(payment_status=Order.PaymentStatus.REFUNDED)
    mark_as_refunded.short_description = _("Mark selected orders as refunded")