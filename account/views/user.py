# SuperAdmin Only Access Views

from rest_framework import viewsets
from django.contrib.auth import get_user_model

from account.renderers import UserRenderer
from ..permissions import IsSuperAdmin
from account.serializers.superadmin import UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    # permission_classes=[IsSuperAdmin]
    pagination_class = None
    queryset = User.objects.all()
    serializer_class = UserSerializer
    renderer_classes = [UserRenderer]

