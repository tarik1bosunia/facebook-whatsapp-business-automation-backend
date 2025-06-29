from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from account.renderers import UserRenderer
from account.serializers import EmailCheckSerializer

from django.contrib.auth import get_user_model

User = get_user_model()


class CheckEmailExistenceAPIView(APIView):
    renderer_classes = [UserRenderer]

    def get(self, request, *args, **kwargs):
        serializer = EmailCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        if User.objects.filter(email=email).exists():
            return Response({'exists': True, 'message': 'An account with this email already exists.'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'exists': False, 'message': 'Email does not exist.'}, status=status.HTTP_200_OK)