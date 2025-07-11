from rest_framework import serializers
from django.contrib.auth import get_user_model

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from account.utils import Util

User = get_user_model()

class ResendVerificationEmailSerializer(serializers.Serializer):
    def validate(self, attrs):
        user = self.context['request'].user
        
        if user.is_email_verified:
            raise serializers.ValidationError(
                {"email": "Email is already verified."}
            )
        return attrs

    def save(self):
        user = self.context['request'].user
        request = self.context['request']
        
        # Generate activation components (matches your registration flow)
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = default_token_generator.make_token(user)
        
        # Build activation link
        frontend_base_url = Util.get_frontend_base_url(request)
        activation_link = f"{frontend_base_url}/activate/{uid}/{token}/"
        
        # Send email (matches your registration flow)
        body = f'Click to verify your email: {activation_link}'
        data = {
            'subject': 'Verify Your Email',
            'body': body,
            'to_email': user.email
        }
        Util.send_email(data)
        
        return {"message": "Verification email sent successfully."}