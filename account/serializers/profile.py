from rest_framework import serializers

from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['id', 'email'] 
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    # todo: need to add validation for id , if the id is not for the current user raise an error

        