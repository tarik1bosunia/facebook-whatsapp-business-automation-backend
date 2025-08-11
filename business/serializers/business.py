from rest_framework import serializers
from ..models import BusinessProfile, BusinessHours


class BusinessHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessHours
        fields = ['id', 'day', 'open_time', 'close_time', 'is_closed']
        read_only_fields = ['id']


class BusinessProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessProfile
        fields = ['id', 'name', 'email', 'phone', 'website', 'description']
        read_only_fields = ['id']
