# views.py
from rest_framework import viewsets, filters, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from customer.models import Customer
from customer.serializers import CustomerSerializer


from customer.serializers import CustomerWithSocialMediaSerializer

class CustomerCreateUpdateView(generics.CreateAPIView, generics.UpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerWithSocialMediaSerializer
    lookup_field = 'id'  # or 'pk', depending on your URL


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().prefetch_related(
        'social_media_users',
        'orders'
    ).order_by('-updated_at')
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'email', 'phone']
    ordering_fields = ['name', 'orders_count', 'total_spent', 'created_at']
    ordering = ['-updated_at']
    pagination_class = None

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_customers = self.get_queryset().count()
        active_customers = self.get_queryset().filter(status='active').count()
        total_revenue = sum(
            customer.total_spent
            for customer in self.get_queryset()
        )

        return Response({
            'totalCustomers': total_customers,
            'activeCustomers': active_customers,
            'totalRevenue': total_revenue,
        })