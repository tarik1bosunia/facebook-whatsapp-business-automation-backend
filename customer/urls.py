from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, CustomerCreateUpdateView, OrderViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('create/', CustomerCreateUpdateView.as_view(), name='customer-create'), # issue when the
    path('customers/<int:id>/', CustomerCreateUpdateView.as_view(), name='customer-update'),
    path('', include(router.urls)),
]