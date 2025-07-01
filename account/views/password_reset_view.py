from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from account.renderers import UserRenderer
from account.serializers.email import SendPasswordResetEmailSerializer
from account.serializers.password import UserPasswordResetConfirmSerializer
from account.utils import Util



class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]
    throttle_scope = 'password_reset'  # Add throttling to prevent abuse

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = getattr(serializer, 'user', None)

        if user and user.is_active:
            # Generate secure tokens
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            
            # Construct reset link
            reset_link = self.generate_reset_link(request, uid, token)
            
            # Send email asynchronously
            self.send_password_reset_email(user, reset_link)

        # Always return same response regardless of email existence
        return Response(
            {'msg': 'If this email is registered, you will receive a password reset link shortly.'},
            status=status.HTTP_200_OK
        )
    
    def generate_reset_link(self, request, uid, token):
        """Construct secure reset link with proper expiration"""
        base_url = Util.get_frontend_base_url(request)
        return f"{base_url}/reset-password/{uid}/{token}/"

    def send_password_reset_email(self, user, reset_link):
        """Send password reset email with proper security context"""
        subject = 'Reset Your Password'
        body = (
            f"You requested a password reset for your account.\n\n"
            f"Please click the following link to reset your password:\n{reset_link}\n\n"
            f"This link will expire in 24 hours.\n"
            f"If you didn't request this, please ignore this email."
        )
        
        
        email_data = {
            'subject': subject,
            'body': body,
            'to_email': user.email
        }
        Util.send_email(email_data)
        
        # Queue email sending to avoid blocking
        # Util.send_email.delay(email_data)  # Assuming Celery or async task  




class UserPasswordResetConfirmView(APIView):
    renderer_classes = [UserRenderer]
    throttle_scope = 'password_reset_confirm'

    def post(self, request, uid=None, token=None, format=None):
        # Validate required parameters
        if not uid or not token:
            return Response(
                {'error': 'Reset token missing in URL.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserPasswordResetConfirmSerializer(
            data=request.data,
            context={'uid': uid, 'token': token}
        )
        
        # Process validation and password reset
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {'msg': 'Password reset successfully. You can now login with your new password.'},
                status=status.HTTP_200_OK
            )
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)