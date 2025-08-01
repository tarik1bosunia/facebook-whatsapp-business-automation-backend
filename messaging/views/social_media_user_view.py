# views.py
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import SocialMediaUser
from ..serializers import SocialMediaUserSerializer
from messaging.enums import PLATFORM

class SocialMediaUserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SocialMediaUserSerializer
    pagination_class = None


    def get_queryset(self):
        return SocialMediaUser.objects.all()
        # return SocialMediaUser.objects.filter(customer__user=self.request.user)

    @action(detail=False, url_path=r'by-platform/(?P<platform>\w+)', methods=['get'])
    def by_platform(self, request, platform=None):
        platform = platform.lower()
        # valid_platforms = [choice[0] for choice in SocialMediaUser.Platform.choices]
        valid_platforms = [choice.value for choice in PLATFORM]

        if platform not in valid_platforms:
            return Response({'error': f'Invalid platform. Valid options: {valid_platforms}'}, status=400)

        queryset = self.get_queryset().filter(platform=platform)

        # TODO: need to give those social media user which are not added any customer
        exclude_customers = request.query_params.get('exclude_customers', 'false').lower() == 'true'
        if exclude_customers:
            queryset = queryset.filter(customer__isnull=True)

        # TODO: Add ordering

        # Add search functionality
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(social_media_id__icontains=search_query) |
                Q(name__icontains=search_query)
            )

        ordering = request.query_params.get('ordering', '-updated_at')
        queryset = queryset.order_by(ordering)    

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)