from rest_framework import serializers


class FacebookAppSerializer(serializers.Serializer):
    app_id = serializers.CharField(max_length=255, required=False)
    app_secret = serializers.CharField(max_length=255, required=False)
    
class FacebookAccessTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField(max_length=500)

    def validate(self, data):
        from business.models.integrations import FacebookIntegration
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context is required for this serializer.")

        user = request.user
        try:
            facebook_integration = FacebookIntegration.objects.get(user=user)
            if not facebook_integration.app_id or not facebook_integration.app_secret:
                raise serializers.ValidationError("Facebook App ID and Secret must be configured before setting the access token.")
        except FacebookIntegration.DoesNotExist:
            raise serializers.ValidationError("Facebook App ID and Secret not configured. Please set them first.")
        return data


class FacebookVerifyTokenSerializer(serializers.Serializer):
    verify_token = serializers.CharField(max_length=100)

class FacebookIntegrationStatusSerializer(serializers.Serializer):
    app_id_set = serializers.BooleanField()
    app_secret_set = serializers.BooleanField()
    long_live_token_set = serializers.BooleanField()
    verify_token_set = serializers.BooleanField()
    is_connected = serializers.BooleanField()
    is_send_auto_reply = serializers.BooleanField()
    is_send_notification = serializers.BooleanField()

class FacebookAutoReplyStatusSerializer(serializers.Serializer):
    is_send_auto_reply = serializers.BooleanField()

class FacebookNotificationStatusSerializer(serializers.Serializer):
    is_send_notification = serializers.BooleanField()

class FacebookConnectionStatusSerializer(serializers.Serializer):
    is_connected = serializers.BooleanField()
