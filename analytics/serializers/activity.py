from rest_framework import serializers
from ..models import Activity

class ActivitySerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()
    
    class Meta:
        model = Activity
        fields = ['id', 'type', 'title', 'description', 'source', 'time']
    
    def get_time(self, obj):
        return obj.time_ago