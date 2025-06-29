from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Order
from ..serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related('customer')
    serializer_class = OrderSerializer
    # permission_classes = [IsAuthenticated]
    pagination_class = None

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'status': ['exact'],
        'payment_status': ['exact'],
        'source': ['exact'],
        'created_at': ['gte', 'lte', 'exact'],
        'customer__id': ['exact'],
    }
    search_fields = ['order_number', 'customer__name', 'customer__phone']
    ordering_fields = ['created_at', 'updated_at', 'total']
    ordering = ['-created_at']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context