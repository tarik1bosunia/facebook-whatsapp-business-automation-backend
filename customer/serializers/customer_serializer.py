

from django.utils.timezone import localtime


from rest_framework import serializers
from customer.models import Customer
from messaging.models import SocialMediaUser

class SocialMediaIDSerializer(serializers.Serializer):
    messenger = serializers.CharField(required=False, max_length=255)
    whatsapp = serializers.CharField(required=False, max_length=255)
    facebook = serializers.CharField(required=False, max_length=255)
    instagram = serializers.CharField(required=False, max_length=255)
    twitter = serializers.CharField(required=False, max_length=255)

class CustomerWithSocialMediaSerializer(serializers.ModelSerializer):
    social_media_ids = SocialMediaIDSerializer(many=True, write_only=True)

    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'social_media_ids']

    def create(self, validated_data):
        social_media_data = validated_data.pop('social_media_ids', [])
        customer = Customer.objects.create(**validated_data)

        self._process_social_media_data(customer, social_media_data)
        return customer

    def update(self, instance, validated_data):
        social_media_data = validated_data.pop('social_media_ids', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        self._process_social_media_data(instance, social_media_data)
        return instance

    def _process_social_media_data(self, customer, social_media_data):
        for item in social_media_data:
            for platform, social_id in item.items():
                try:
                    sm_user = SocialMediaUser.objects.get(
                        platform=platform,
                        social_media_id=social_id
                    )
                    # Update the existing one
                    sm_user.customer = customer
                    sm_user.name = customer.name
                    sm_user.save(update_fields=['customer', 'name'])
                except SocialMediaUser.DoesNotExist:
                    raise serializers.ValidationError({
                        "social_media_ids": f"Invalid social media ID '{social_id}' for platform '{platform}'."
                    })


class SocialMediaUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaUser
        fields = ['platform', 'avatar_url']


class CustomerSerializer(serializers.ModelSerializer):
    lastOrderDate = serializers.SerializerMethodField()
    channel = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    # social_media = SocialMediaUserSerializer(many=True, source='social_media_users')

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'email', 'phone', 'createdAt', 'orders_count',
            'total_spent', 'lastOrderDate', 'status', 'channel', 'avatar',
            # 'social_media'
        ]
        extra_kwargs = {
            'createdAt': {'source': 'created_at'},
        }

    def get_lastOrderDate(self, obj):
        last_order = obj.orders.order_by('-created_at').first()
        if last_order:
            return localtime(last_order.created_at).strftime("%b %d, %Y")
        return None

    def get_channel(self, obj):
        platforms = set(smu.platform for smu in obj.social_media_users.all())
        if len(platforms) > 1:
            return 'both'
        return platforms.pop() if platforms else 'unknown'

    def get_avatar(self, obj):
        # First try to get avatar from social media accounts
        social_avatar = obj.social_media_users.filter(avatar_url__isnull=False).first()
        if social_avatar:
            return social_avatar.avatar_url

        # Fallback to default avatar based on name
        return f"https://i.pravatar.cc/150?u={obj.name}"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Format the total_spent as float instead of string
        data['total_spent'] = float(data['total_spent'])
        # Format the created_at date
        data['createdAt'] = localtime(instance.created_at).strftime("%Y-%m-%dT%H:%M:%S")
        return data