from rest_framework import serializers
from .models import SocialMediaUser, Conversation, ChatMessage



class SocialMediaUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaUser
        fields = '__all__'

class ConversationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')
    customer = serializers.SerializerMethodField()
    lastMessage = serializers.SerializerMethodField()
    unreadCount = serializers.SerializerMethodField()
    channel = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'customer', 'auto_reply', 'lastMessage', 'channel', 'unreadCount']

    def get_customer(self, obj):
        socialuser = obj.socialuser
        return {
            'id': socialuser.id,
            'name': socialuser.name,
            'avatar': socialuser.avatar_url
        }

    def get_lastMessage(self, obj):
        last_msg = obj.last_message()
        if last_msg:
            return {
                'text': last_msg.message,
                'time': last_msg.created_at,
                'isRead': last_msg.is_read
            }
        return None

    def get_unreadCount(self, obj):
        return obj.unread_count()

    def get_channel(self, obj):
        return obj.socialuser.platform

class ChatMessageSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source='message')
    time = serializers.DateTimeField(source='updated_at')
    media_url = serializers.SerializerMethodField()
    class Meta:
        model = ChatMessage
        fields = ['id', 'text', 'time', 'sender', 'media_id', 'media_type', 'contacts', 'media_url']
    def get_media_url(self, obj):
        """
        Returns media URL with priority order:
        1. The locally stored messenger_media_file if it exists (most reliable)
        2. The messenger_media_url as fallback (might expire)
        3. None if neither exists
        """
        if obj.messenger_media_file:
            return self.context['request'].build_absolute_uri(obj.messenger_media_file.url)
        elif obj.messenger_media_url:
            return obj.messenger_media_url
        return None


class AutoReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'auto_reply']
        read_only_fields = ['id']