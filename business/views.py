# views.py
from rest_framework import viewsets, permissions, status, generics, filters
from business.models import BusinessProfile, BusinessHours
from .serializers import BusinessProfileSerializer, BusinessHoursSerializer
from rest_framework.response import Response

from rest_framework.exceptions import ValidationError

class BusinessProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = BusinessProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        try:
            return user.business
        except BusinessProfile.DoesNotExist:
            return None
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance, data=request.data)
        else:
            serializer = self.get_serializer(data={**request.data, 'user': request.user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)

    # def retrieve(self, request):
    #     profile = self.get_object()
    #     if not profile:
    #         return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    #     serializer = BusinessProfileSerializer(profile)
    #     return Response(serializer.data)
    


    # def create(self, request):
    #     if self.get_object():
    #         return Response({'detail': 'Profile already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    #     serializer = BusinessProfileSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(user=request.user)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def update(self, request):
    #     profile = self.get_object()
    #     if not profile:
    #         return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    #     serializer = BusinessProfileSerializer(profile, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data)


class BusinessHoursViewSet(viewsets.ModelViewSet):
    serializer_class = BusinessHoursSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    

    def get_queryset(self):
        return BusinessHours.objects.filter(business__user=self.request.user)

    def perform_create(self, serializer):
        business = BusinessProfile.objects.get(user=self.request.user)
        day = serializer.validated_data['day']
        instance, created = BusinessHours.objects.update_or_create(
            business=business,
            day=day,
            defaults={
                'open_time': serializer.validated_data.get('open_time'),
                'close_time': serializer.validated_data.get('close_time'),
                'is_closed': serializer.validated_data.get('is_closed', False),
            }
        )
        serializer.instance = instance

    # DEBUG
    # def create(self, request, *args, **kwargs):
    #     print("🔍 Incoming data to create():", request.data)
    #     return super().create(request, *args, **kwargs)

    # def update(self, request, *args, **kwargs):
    #     print("🔍 Incoming data to update():", request.data)
    #     return super().update(request, *args, **kwargs)    




 # integrations/views.py

from .models import FacebookIntegration, WhatsAppIntegration
from .serializers import FacebookIntegrationSerializer, WhatsAppIntegrationSerializer

# integrations/views.py

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK


class BaseIntegrationView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model_class = None  # Must be set by subclass

    def get_object(self):
        # Ensure configuration exists for the user
        config, created = self.model_class.objects.get_or_create(user=self.request.user)
        return config

    def put(self, request, *args, **kwargs):
        """Allow full updates (overwrites all fields except timestamps/user)"""
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """Allow partial updates (single field or a few)"""
        return self.partial_update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Return the current integration config"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=HTTP_200_OK)



class FacebookIntegrationView(BaseIntegrationView):
    serializer_class = FacebookIntegrationSerializer
    model_class = FacebookIntegration


class WhatsAppIntegrationView(BaseIntegrationView):
    serializer_class = WhatsAppIntegrationSerializer
    model_class = WhatsAppIntegration


#  Procut

from .models import ProductCategory, Product
from .serializers import ProductCategorySerializer, ProductSerializer
from account.renderers import UserRenderer
from account.permissions import IsBusinessman
from django_filters.rest_framework import DjangoFilterBackend

class ProductCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = ProductCategorySerializer
    permission_classes = [IsBusinessman]
    renderer_classes = [UserRenderer]
    pagination_class = None

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['name']


    def get_queryset(self):
        return ProductCategory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsBusinessman]
    renderer_classes = [UserRenderer]
    pagination_class = None

    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    filterset_fields = ['category', 'stock']
    ordering_fields = ['price', 'stock', 'created_at']

    
    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

