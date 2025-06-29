from rest_framework import serializers
from .models import Category, FAQ

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'user']
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category']



class FAQsWithCategorySerializer(serializers.ModelSerializer):
    faqs = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'faqs']

    def get_faqs(self, obj):
        faqs = getattr(obj, 'prefetched_faqs', [])    
        return FAQSerializer(faqs, many=True).data

