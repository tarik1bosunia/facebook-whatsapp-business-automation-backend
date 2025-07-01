from rest_framework import serializers


class EmailCheckSerializer(serializers.Serializer):
    email = serializers.EmailField()
