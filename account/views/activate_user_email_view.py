from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response


from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

from account.renderers import UserRenderer

User = get_user_model()

class ActivateUserEmailView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [AllowAny]
    
    def get(self, request, uid, token):
        try:
            # Decode the uid
            uid = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uid)

            # Check if the token is valid
            if default_token_generator.check_token(user, token):
                user.is_email_verified = True  
                user.save()
                return Response({'message': 'Email successfully verified'}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid activation link'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid activation link'}, status=status.HTTP_400_BAD_REQUEST)