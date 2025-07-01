from rest_framework import serializers

from django.contrib.auth import get_user_model

User = get_user_model()


class UserDeleteAccountSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        email = attrs['email']
        password = attrs['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'User with this email does not exist'})
        
        if not user.check_password(password):
            raise serializers.ValidationError({'password': 'Incorrect password'})
        
        attrs['user'] = user
        return attrs
    