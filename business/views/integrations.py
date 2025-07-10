from ..models import FacebookIntegration, WhatsAppIntegration
from ..serializers import FacebookIntegrationSerializer, WhatsAppIntegrationSerializer

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from account.permissions import IsAuthenticatedAndVerified
from account.renderers import UserRenderer

class BaseIntegrationView(generics.RetrieveUpdateAPIView):
    """
    Base view for platform integrations
    """
    permission_classes = [IsAuthenticatedAndVerified]
    model_class = None  # Must be set by subclass

    def get_queryset(self):
        if self.model_class is None:
            raise NotImplementedError("model_class must be defined")
        return self.model_class.objects.filter(user=self.request.user)

    def get_object(self):
        # Ensure configuration exists for the user
        obj, created = self.model_class.objects.get_or_create(
            user=self.request.user,
            defaults={'is_connected': False},
        )
        return obj
    
    def perform_update(self, serializer):
        # Ensure user can't be changed
        serializer.save(user=self.request.user)

    def get(self, request, *args, **kwargs):
        """Get current integration configuration"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=HTTP_200_OK)    

    def put(self, request, *args, **kwargs):
        """Allow full updates (overwrites all fields except timestamps/user)"""
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """Allow partial updates (single field or a few)"""
        return self.partial_update(request, *args, **kwargs)




class FacebookIntegrationView(BaseIntegrationView):
    serializer_class = FacebookIntegrationSerializer
    model_class = FacebookIntegration


class WhatsAppIntegrationView(BaseIntegrationView):
    serializer_class = WhatsAppIntegrationSerializer
    model_class = WhatsAppIntegration
