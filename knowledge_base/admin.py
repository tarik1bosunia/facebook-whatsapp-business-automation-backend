from django.contrib import admin
from .models import Category, FAQ

class FAQInline(admin.TabularInline):
    model = FAQ
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user')
    search_fields = ('name',)
    inlines = [FAQInline]

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'answer', 'category')
    search_fields = ('question', 'answer')
    list_filter = ('category',)
