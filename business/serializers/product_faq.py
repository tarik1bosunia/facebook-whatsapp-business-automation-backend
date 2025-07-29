from rest_framework import serializers
from business.models import ProductFAQ

class ProductFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFAQ
        fields = ['id', 'product', 'question', 'answer']
        read_only_fields = ['id']