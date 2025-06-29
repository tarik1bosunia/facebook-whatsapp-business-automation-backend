# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessProfileView, BusinessHoursViewSet, ProductCategoryViewSet, ProductViewSet
from .views import FacebookIntegrationView, WhatsAppIntegrationView



router = DefaultRouter()
router.register(r'business-hours', BusinessHoursViewSet, basename='business-hours')
router.register(r'categories', ProductCategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('business-profile/', BusinessProfileView.as_view(), name='business-profile'),
    path('facebook/', FacebookIntegrationView.as_view(), name='facebook-integration'),
    path('whatsapp/', WhatsAppIntegrationView.as_view(), name='whatsapp-integration'),
    
    path('', include(router.urls)),
]
