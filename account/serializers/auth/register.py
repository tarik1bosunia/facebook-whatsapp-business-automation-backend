from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', ]
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,  # Enforce minimum length
            }
        }

    def validate_password(self, value):
        validate_password(value)
        return value
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)



