from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import SocialMediaUser, Conversation, ChatMessage


@admin.register(SocialMediaUser)
class SocialMediaUserAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'platform',
        'social_media_id',
        'customer_link',
        'avatar_preview',
        'customer',
        'created_at'
    ]
    list_filter = ['platform', 'created_at']
    search_fields = ['name', 'social_media_id', 'customer__name']
    readonly_fields = ['created_at', 'updated_at', 'avatar_preview', 'customer_link']
    fieldsets = (
        (_('Social Media Information'), {
            'fields': ('name', 'platform', 'social_media_id', 'avatar_url', 'customer_link', 'customer',)
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at')
        }),
        (_('Avatar Preview'), {
            'fields': ('avatar_preview',)
        }),
    )
    list_select_related = ['customer']
    date_hierarchy = 'created_at'
    list_per_page = 20

    def customer_link(self, obj):
        if obj.customer:
            url = f"/admin/customer/customer/{obj.customer.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.customer.name)
        return "-"

    customer_link.short_description = _('Customer')

    def avatar_preview(self, obj):
        if obj.avatar_url:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.avatar_url)
        return "-"

    avatar_preview.short_description = _('Avatar Preview')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'socialuser','auto_reply', 'created_at', 'updated_at')
    list_filter = ('auto_reply', 'created_at', 'updated_at')
    search_fields = ('auto_reply', 'socialuser__name', 'socialuser__social_media_id')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('socialuser',)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'truncated_message','media_id', 'media_type', 'contacts', 'is_read', 'sender', 'created_at', 'updated_at')
    list_filter = ('sender', 'is_read', 'created_at')
    search_fields = ('message', 'conversation__socialuser__name')
    readonly_fields = ('created_at',)

    def truncated_message(self, obj):
        if obj.message:
            return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
        return "[No message]"

    truncated_message.short_description = 'Message'  # type: ignore[attr-defined]
