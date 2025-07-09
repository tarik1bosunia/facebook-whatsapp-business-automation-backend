
from rest_framework import serializers


# service
from ..models import Service


class ServiceSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Service
        fields = [
            'id',
            'user',
            'user_email',
            'name',
            'description',
            'base_price',
            'duration_minutes',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'base_price': {'min_value': 0},
            'duration_minutes': {'min_value': 1}
        }

    def create(self, validated_data):
        # Automatically set the current user as the service provider
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)