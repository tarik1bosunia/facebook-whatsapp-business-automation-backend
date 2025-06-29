from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import CreateAPIView

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError


from account.renderers import UserRenderer
from account.serializers import UserRegistrationSerializer
from account.utils import Util


class UserRegistrationView(CreateAPIView):
    renderer_classes = [UserRenderer]
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()

            token = Util.get_tokens_for_user(user)

            # generate activation components
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token_activate_email = default_token_generator.make_token(user)

            # get forntend URL and build activation link
            try:
                frontend_base_url = Util.get_frontend_base_url(request)
                activation_link = f"{frontend_base_url}/activate/{uid}/{token_activate_email}/"
                # Email content
                body = f'Click to verify your email: {activation_link}'
                data = {
                    'subject': 'Verify Your Email',
                    'body': body,
                    'to_email': user.email
                }
                Util.send_email(data)

                return Response({
                    'token': token,
                    "user": {
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "role": user.role,
                    },
                    'message': 'Registration Successful. Please check your email.'

                }, status=status.HTTP_201_CREATED)

            except ValidationError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
