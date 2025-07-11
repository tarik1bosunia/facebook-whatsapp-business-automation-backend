
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from account.utils import Util

User = get_user_model()

class UserVerificationStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        is_verified = Util.is_user_verified(user)
        return Response({
            'is_verified': is_verified,
            'auth_provider': user.auth_provider
        })