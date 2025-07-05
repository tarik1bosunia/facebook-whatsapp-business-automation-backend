from django.contrib import admin
from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'type', 'source',  'created_at', 'time_ago')
    list_filter = ('type', 'source', 'created_at')
    search_fields = ('title', 'description', 'user__email')
    readonly_fields = ('created_at', 'time_ago')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'type', 'source', 'user')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'time_ago')
        }),
    )

    def has_add_permission(self, request):
        return True  # Allow adding from admin if needed

    def has_change_permission(self, request, obj=None):
        return True  # Allow editing

    def has_delete_permission(self, request, obj=None):
        return True  # Allow deletion

