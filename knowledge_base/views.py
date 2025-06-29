from django.db.models import Q, Prefetch
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Category, FAQ
from .serializers import CategorySerializer, FAQSerializer, FAQsWithCategorySerializer
from django_filters.rest_framework import DjangoFilterBackend

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    pagination_class = None

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)
    
    

class FAQViewSet(viewsets.ModelViewSet):
    serializer_class = FAQSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'question']

    def get_queryset(self):
        return FAQ.objects.filter(category__user=self.request.user)
    
    def perform_create(self, serializer):
        category = serializer.validated_data['category']
        if category.user != self.request.user:
            raise PermissionDenied("You don't own this category")
        serializer.save()


class FAQsWithCategoriesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FAQsWithCategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        search = self.request.query_params.get('search', '')
        queryset = Category.objects.filter(user=self.request.user).prefetch_related(
            Prefetch('faqs', 
                    queryset=FAQ.objects.all(),
                    to_attr='prefetched_faqs')
        )

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(faqs__question__icontains=search) |
                Q(faqs__answer__icontains=search)
            ).distinct()

        return queryset
    


"""
select_related works by doing a SQL JOIN (good for foreign key and one-to-one)
prefetch_related does a separate lookup (good for many-to-many and reverse foreign key)
"""        