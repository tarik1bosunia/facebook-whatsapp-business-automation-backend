from rest_framework import generics
from ..models import Activity
from ..serializers import ActivitySerializer
from rest_framework.permissions import IsAuthenticated
from utils.pagination import CustomPageNumberPagination

class ActivityListAPIView(generics.ListAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    
    def get_queryset(self):
        # You can customize this queryset  filter by current user
        return Activity.objects.filter(user=self.request.user)