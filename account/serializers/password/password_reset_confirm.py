from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from django.utils.encoding import  smart_str, DjangoUnicodeDecodeError
from django.utils.http import  urlsafe_base64_decode
from django.utils import timezone
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from django.contrib.auth import get_user_model

User = get_user_model()

class UserPasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255,
        style={'input_type': 'password'},
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        max_length=255,
        style={'input_type': 'password'},
        write_only=True,
        required=True
    )

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        
        # Validate password match
        if password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })

        # Get context data
        uid = self.context.get('uid')
        token = self.context.get('token')
        
        if not uid or not token:
            raise serializers.ValidationError({
                'token': 'Missing reset token in request.'
            })

        try:
            # Decode user ID safely
            user_id = smart_str(urlsafe_base64_decode(uid))
            self.user = User.objects.get(id=user_id, is_email_verified=True)
        except (TypeError, ValueError, OverflowError, DjangoUnicodeDecodeError, User.DoesNotExist):
            raise serializers.ValidationError({
                'token': 'Invalid or expired reset link.'
            })

        # Validate token and check if password was changed after token generation
        token_generator = PasswordResetTokenGenerator()
        
        # Check if token is still valid
        if not token_generator.check_token(self.user, token):
            raise serializers.ValidationError({
                'token': 'Invalid or expired reset link.'
            })
            
        # Check if password was changed after token was generated
        if self.user.last_password_change:
            token_created_at = token_generator.get_token_timestamp(self.user, token)
            if token_created_at < self.user.last_password_change.timestamp():
                raise serializers.ValidationError({
                    'token': 'This reset link has already been used.'
                })

        return attrs

    def save(self, **kwargs):
        password = self.validated_data['password']
        self.user.set_password(password)
        
        # Update password change timestamp
        self.user.last_password_change = timezone.now()
        self.user.save(update_fields=['password', 'last_password_change'])
