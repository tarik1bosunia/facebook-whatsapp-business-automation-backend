from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from rest_framework_simplejwt.views import (
    TokenObtainPairView as TokenObtainPairViewJWT,
    TokenRefreshView as TokenRefreshViewJWT,
)

from account.renderers import UserRenderer
from account.serializers.auth import CustomTokenObtainPairSerializer
from account.utils import Util


class TokenObtainPairView(TokenObtainPairViewJWT):
    serializer_class = CustomTokenObtainPairSerializer
    renderer_classes = [UserRenderer]

class TokenRefreshView(TokenRefreshViewJWT):
    renderer_classes = [UserRenderer]    


class VerifyUserView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        token = Util.get_tokens_for_user(request.user)
        return Response({'token': token, "message": "User is verified"}, status=status.HTTP_200_OK)