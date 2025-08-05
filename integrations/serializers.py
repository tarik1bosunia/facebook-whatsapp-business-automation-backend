from rest_framework import serializers


class FacebookAppSerializer(serializers.Serializer):
    app_id = serializers.CharField(max_length=255, required=False)
    app_secret = serializers.CharField(max_length=255, required=False)
    
class FacebookAccessTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField(max_length=500)

class FacebookVerifyTokenSerializer(serializers.Serializer):
    verify_token = serializers.CharField(max_length=100)