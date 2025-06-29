from rest_framework import generics
from django.contrib.auth import get_user_model

from account.serializers import UserSerializer

User = get_user_model()

class UserListView(generics.ListAPIView):
    pagination_class = None
    queryset = User.objects.all()
    serializer_class = UserSerializer