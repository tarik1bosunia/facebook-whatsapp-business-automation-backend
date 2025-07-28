# apps/llm_integration/api/urls.py
from django.urls import path
from .views import LLMAssistantAPI

urlpatterns = [
    path('assistant/', LLMAssistantAPI.as_view(), name='llm-assistant'),
]