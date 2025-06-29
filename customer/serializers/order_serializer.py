from rest_framework import serializers
from ..models import Order, Customer


class CustomerOrderSerializer(serializers.ModelSerializer):

    avatar = serializers.SerializerMethodField(read_only=True)

    def get_avatar(self, obj):
        # First try to get avatar from social media accounts
        social_avatar = obj.social_media_users.filter(avatar_url__isnull=False).first()
        if social_avatar:
            return social_avatar.avatar_url

        # Fallback to default avatar based on name
        return f"https://i.pravatar.cc/150?u={obj.name}"

    class Meta:
        model = Customer
        fields = ['id', 'name', 'avatar']



class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerOrderSerializer()
    orderNumber = serializers.CharField(source='order_number')
    date = serializers.DateTimeField(source='created_at', format='%Y-%m-%d %H:%M:%S')
    paymentStatus = serializers.CharField(source='payment_status')

    class Meta:
        model = Order
        fields = [
            'id',
            'orderNumber',
            'customer',
            'date',
            'items',
            'total',
            'status',
            'source',
            'paymentStatus'
        ]