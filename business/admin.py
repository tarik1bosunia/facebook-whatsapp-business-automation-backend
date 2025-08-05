# admin.py
from django.contrib import admin
from business.models import BusinessProfile, BusinessHours

class BusinessHoursInline(admin.TabularInline):
    model = BusinessHours
    extra = 1

   

@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'email', 'phone', 'website']
    search_fields = ['name', 'email', 'phone', 'user__username']
    inlines = [BusinessHoursInline]

@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ['id', 'business', 'day', 'open_time', 'close_time', 'is_closed']
    list_filter = ['day', 'is_closed']
    search_fields = ['business__name']


from .models import ProductCategory, Product, ProductFAQ

class ProductFAQInline(admin.TabularInline):
    model = ProductFAQ
    extra = 1 

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'created_at')
    search_fields = ('name',)
    list_filter = ('user',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'user', 'price', 'stock', 'created_at')
    search_fields = ('name',)
    list_filter = ('category', 'user')
    inlines = [ProductFAQInline]


@admin.register(ProductFAQ)
class ProductFAQAdmin(admin.ModelAdmin):
    list_display = ('product', 'question')
    search_fields = ('question', 'product__name')

from .models import FacebookIntegration, WhatsAppIntegration


@admin.register(FacebookIntegration)
class FacebookIntegrationAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'app_id',
        'app_secret',
        'platform_id',
        'verify_token',
        'is_connected',
        'is_send_auto_reply',
        'is_send_notification',
        'created_at',
        'updated_at',
    )
    search_fields = ('user__email', 'platform_id', 'verify_token')
    list_filter = ('is_connected', 'is_send_auto_reply', 'is_send_notification')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(WhatsAppIntegration)
class WhatsAppIntegrationAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'platform_id',
        'verify_token',
        'is_connected',
        'is_send_auto_reply',
        'is_send_notification',
        'created_at',
        'updated_at',
    )
    search_fields = ('user__email', 'platform_id', 'verify_token')
    list_filter = ('is_connected', 'is_send_auto_reply', 'is_send_notification')
    readonly_fields = ('created_at', 'updated_at')


from .models import Promotion

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "discount_percent",
        "start_date",
        "end_date",
        "is_active",
        "is_current",
    )
    list_filter = ("is_active", "start_date", "end_date")
    search_fields = ("title", "description", "user__email", "user__username")
    date_hierarchy = "start_date"
    ordering = ("-start_date",)

    def is_current(self, obj):
        return obj.is_current()
    is_current.boolean = True  # ✅ Adds a green checkmark in admin
    is_current.short_description = "Currently Active"

