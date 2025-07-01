from rest_framework import serializers

from django.contrib.auth import get_user_model

User = get_user_model()

class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    
    def validate_email(self, value):
        """Validate email format and existence without leaking information"""
        try:
            # Perform case-insensitive matching
            self.user = User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            # Don't reveal whether email exists in the system
            pass
        return value