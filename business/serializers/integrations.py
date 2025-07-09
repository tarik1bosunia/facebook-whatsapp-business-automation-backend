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
        is_connected = data.get(
            'is_connected',
            self.instance.is_connected if self.instance else False
        )

        if is_connected:
            errors = {}
            
            # Required fields when integration is active
            required_fields = ['platform_id', 'access_token', 'verify_token']
            for field in required_fields:
                if field in data:
                    if data[field] == '' and (not self.instance or not getattr(self.instance, field)):
                        errors[field] = f"Required when integration is active"
                elif not self.instance or not getattr(self.instance, field):
                    errors[field] = f"Required when integration is active"

            if errors:
                raise serializers.ValidationError(errors)
                
        return data 
    
    def update(self, instance, validated_data):
        # Clean up tokens if empty string is passed
        if 'access_token' in validated_data and validated_data['access_token'] == '':
            validated_data.pop('access_token')
        if 'verify_token' in validated_data and validated_data['verify_token'] == '':
            validated_data.pop('verify_token')
        return super().update(instance, validated_data)    


class FacebookIntegrationSerializer(BaseIntegrationSerializer):
    class Meta(BaseIntegrationSerializer.Meta):
        model = FacebookIntegration


class WhatsAppIntegrationSerializer(BaseIntegrationSerializer):
    class Meta(BaseIntegrationSerializer.Meta):
        model = WhatsAppIntegration