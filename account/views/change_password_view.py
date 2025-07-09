from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from account.permissions import IsAuthenticatedAndVerified

from account.renderers import UserRenderer
from account.serializers.password import UserChangePasswordSerializer


class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticatedAndVerified]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(
            data=request.data,
            context={'user': request.user}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': 'Password Changed Successfully.'},
            status=status.HTTP_200_OK
        )

