from rest_framework import serializers
from .models import AIConfiguration, AIModel

class AIModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModel
        fields = ['id', 'code', 'name', 'is_custom']

class AIConfigurationSerializer(serializers.ModelSerializer):
    api_key = serializers.CharField(
        write_only=True, 
        required=False, 
        allow_blank=True,
        style={'input_type': 'password'}
    )

    ai_model = serializers.PrimaryKeyRelatedField(
        queryset=AIModel.objects.all()
    )

    class Meta:
        model = AIConfiguration
        exclude = ['created_at', 'updated_at', 'user']

    def update(self, instance, validated_data):
        if 'api_key' in validated_data and validated_data['api_key'] == '':
            validated_data.pop('api_key')
        return super().update(instance, validated_data)    