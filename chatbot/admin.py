from django.contrib import admin
from .models import AIConfiguration, AIModel


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_custom')
    search_fields = ('name', 'code')
    ordering = ('name',)



@admin.register(AIConfiguration)
class AIConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'ai_model',
        'response_tone',
        'auto_respond',
        'generate_suggestions',
        'human_handoff',
        'learn_from_history',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'ai_model',
        'response_tone',
        'auto_respond',
        'generate_suggestions',
        'human_handoff',
        'learn_from_history',
    )
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'ai_model__name')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['user', 'ai_model']

    fieldsets = (
        (None, {
            'fields': ('user', 'ai_model', 'response_tone', 'brand_persona', 'api_key')
        }),
        ('Features', {
            'fields': (
                'auto_respond',
                'generate_suggestions',
                'human_handoff',
                'learn_from_history',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
