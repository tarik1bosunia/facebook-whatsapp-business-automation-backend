from rest_framework import viewsets
from business.models import ProductFAQ
from business.serializers import ProductFAQSerializer
from account.permissions import IsAuthenticatedAndVerified
from rest_framework.exceptions import PermissionDenied

from utils.renderers import CustomRenderer

class ProductFAQViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedAndVerified]
    serializer_class = ProductFAQSerializer
    pagination_class = None  
    renderer_classes = [CustomRenderer] 

    def get_queryset(self):
        queryset = ProductFAQ.objects.filter(product__user=self.request.user)
        
        # Filter by product id if ?product=1 is provided
        product_id = self.request.query_params.get("product")
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset
    
    def perform_create(self, serializer):
        product = serializer.validated_data.get('product')
        if product and product.user != self.request.user:
            raise PermissionDenied("You cannot add FAQs to another user's product.")
        serializer.save()