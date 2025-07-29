# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessProfileView, BusinessHoursViewSet, ProductCategoryViewSet, ProductViewSet, ProductFAQViewSet
from .views import FacebookIntegrationView, WhatsAppIntegrationView



router = DefaultRouter()
router.register(r'business-hours', BusinessHoursViewSet, basename='business-hours')
router.register(r'categories', ProductCategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'product-faqs', ProductFAQViewSet, basename='product-faq')

# app_name = 'integrations'

urlpatterns = [
    path('', include(router.urls)),
    path('business-profile/', BusinessProfileView.as_view(), name='business-profile'),
    path('facebook-integration/', FacebookIntegrationView.as_view(), name='facebook-integration'),
    path('whatsapp-integration/', WhatsAppIntegrationView.as_view(), name='whatsapp-integration'),
    
]
