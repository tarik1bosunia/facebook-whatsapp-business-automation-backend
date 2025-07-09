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