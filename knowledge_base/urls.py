from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, FAQViewSet, FAQsWithCategoriesViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'faqs', FAQViewSet, basename='faqs')
router.register(r'faqs-with-categories', FAQsWithCategoriesViewSet, basename='faqs-with-categories')

urlpatterns = [
    path('', include(router.urls)),
]
