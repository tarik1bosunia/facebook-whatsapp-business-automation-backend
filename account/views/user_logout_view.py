from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken


from account.renderers import UserRenderer


class UserLogoutView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'errors': {'refresh': 'this field is required!'}},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({'message': 'Logout successful. Token blacklisted.'},
                            status=status.HTTP_205_RESET_CONTENT)

        except Exception as e:
            return Response({'errors': {"non_field_erros": [str(e)]}},
                            status=status.HTTP_400_BAD_REQUEST)