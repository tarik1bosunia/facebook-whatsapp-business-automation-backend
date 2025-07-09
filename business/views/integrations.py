from ..models import FacebookIntegration, WhatsAppIntegration
from ..serializers import FacebookIntegrationSerializer, WhatsAppIntegrationSerializer

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