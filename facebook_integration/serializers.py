from rest_framework import serializers

class FacebookAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField(max_length=500)