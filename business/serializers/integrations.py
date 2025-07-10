from rest_framework import serializers

from ..models import FacebookIntegration, WhatsAppIntegration

class BaseIntegrationSerializer(serializers.ModelSerializer):
    access_token = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={'input_type': 'password'},
        help_text="Leave blank to keep existing token"
    )
    
    
    class Meta:
        # Model will be defined in child serializer
        exclude = ['created_at', 'updated_at', 'user']

        extra_kwargs = {
            'platform_id': {'required': False},
            'verify_token': {'write_only': True, 'required': False}
        }

    def validate(self, data):
        """Ensure required fields are provided when is_connected=True"""
        is_connected = data.get('is_connected', False)
        is_creating = self.instance is None

        if is_creating and is_connected:
            missing_fields = [
                field for field in ['platform_id', 'access_token', 'verify_token']
                if field not in data or not data[field]
            ]

            if missing_fields:
                raise serializers.ValidationError({
                    field: "This field is required when creating a connected integration"
                    for field in missing_fields
                })

        # For updates: Only validate if changing to connected state
        elif not is_creating and is_connected and not self.instance.is_connected:
            missing_fields = [
                field for field in ['platform_id', 'access_token', 'verify_token']
                if not getattr(self.instance, field) and field not in data
            ]
            if missing_fields:
                raise serializers.ValidationError({
                    field: "Required to activate integration"
                    for field in missing_fields
                })
        
        return data 
    
    def update(self, instance, validated_data):
        # Handle empty strings - treat as "keep existing value"
        for field in ['platform_id', 'access_token', 'verify_token']:
            if field in validated_data and validated_data[field] == '':
                validated_data.pop(field)
        
        return super().update(instance, validated_data)  
    
    def to_representation(self, instance):
        """Mask sensitive fields in responses"""
        data = super().to_representation(instance)
        if instance.access_token:
            data['access_token'] = '********'
        if instance.verify_token:
            data['verify_token'] = '********'
        return data


class FacebookIntegrationSerializer(BaseIntegrationSerializer):
    class Meta(BaseIntegrationSerializer.Meta):
        model = FacebookIntegration


class WhatsAppIntegrationSerializer(BaseIntegrationSerializer):
    class Meta(BaseIntegrationSerializer.Meta):
        model = WhatsAppIntegration