

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
        fields = ['name', 'phone', 'city', 'police_station', 'area', 'social_media_ids']

    def create(self, validated_data):
        social_media_data = validated_data.pop('social_media_ids', [])
        user = self.context['request'].user
        customer = Customer.objects.create(user=user, **validated_data)

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
                    if sm_user.customer and sm_user.customer != customer:
                        raise serializers.ValidationError({
                            "social_media_ids": f"Social media ID '{social_id}' for platform '{platform}' is already linked to another customer."
                        })
                    else:
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
    last_order_date = serializers.SerializerMethodField()
    channel = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'phone', 'city', 'police_station', 'area', 'orders_count',
            'total_spent', 'status', 'avatar', 'channel', 'last_order_date', 'created_at', 'updated_at',
        ]

    def get_last_order_date(self, obj):
        last_order = obj.orders.order_by('-created_at').first()
        return localtime(last_order.created_at).isoformat() if last_order else None

    def get_channel(self, obj):  # method name matches field 'channel'
        platforms = set(smu.platform for smu in obj.social_media_users.all())
        if len(platforms) > 1:
            return 'both'
        return platforms.pop() if platforms else 'unknown'

    def get_avatar(self, obj):
        social_avatar = obj.social_media_users.filter(avatar_url__isnull=False).first()
        if social_avatar:
            return social_avatar.avatar_url
        return f"https://i.pravatar.cc/150?u={obj.name}"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['total_spent'] = float(data['total_spent'])
        return data