
from rest_framework import serializers
from business.models import BusinessProfile, BusinessHours

class BusinessHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessHours
        fields = ['id', 'day', 'open_time', 'close_time', 'is_closed']

class BusinessProfileSerializer(serializers.ModelSerializer):
    hours = BusinessHoursSerializer(many=True, read_only=True)

    class Meta:
        model = BusinessProfile
        fields = ['id', 'name', 'email', 'phone', 'website', 'description', 'hours']



# integrations

from .models import FacebookIntegration, WhatsAppIntegration

class BaseIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        # Model will be defined in child serializer
        exclude = ['created_at', 'updated_at', 'user']
    
    def update(self, instance, validated_data):
        if 'access_token' in validated_data and validated_data['access_token'] == '':
            validated_data.pop('access_token')
        return super().update(instance, validated_data)    


class FacebookIntegrationSerializer(BaseIntegrationSerializer):
    class Meta(BaseIntegrationSerializer.Meta):
        model = FacebookIntegration


class WhatsAppIntegrationSerializer(BaseIntegrationSerializer):
    class Meta(BaseIntegrationSerializer.Meta):
        model = WhatsAppIntegration




from .models import ProductCategory, Product

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        # Automatically set the user from the request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'category', 'name', 'description', 'price', 'stock', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


    def create(self, validated_data):
        # Automatically set the user from the request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# service
from .models import Service


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