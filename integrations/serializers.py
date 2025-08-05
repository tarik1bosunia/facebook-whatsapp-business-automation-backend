from rest_framework import serializers

class FacebookAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField(max_length=500)
    app_id = serializers.CharField(max_length=255, required=False)
    app_secret = serializers.CharField(max_length=255, required=False)