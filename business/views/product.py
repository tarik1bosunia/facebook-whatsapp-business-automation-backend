from rest_framework.viewsets import ModelViewSet
from rest_framework import filters

from utils.pagination import CustomPageNumberPagination
from ..models import ProductCategory, Product
from ..serializers import ProductCategorySerializer, ProductSerializer
from account.renderers import UserRenderer
from account.permissions import IsBusinessman, IsAuthenticatedAndVerified
from django_filters.rest_framework import DjangoFilterBackend

class ProductCategoryViewSet(ModelViewSet):
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticatedAndVerified]
    renderer_classes = [UserRenderer]
    pagination_class = None

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['name']


    def get_queryset(self):
        return ProductCategory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedAndVerified]
    renderer_classes = [UserRenderer]
    pagination_class = CustomPageNumberPagination

    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    filterset_fields = ['category', 'stock']
    ordering_fields = ['price', 'stock', 'created_at']

    
    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)