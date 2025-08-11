from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from ..models import BusinessProfile, BusinessHours
from ..serializers import BusinessProfileSerializer, BusinessHoursSerializer
from account.permissions import IsAuthenticatedAndVerified


class BusinessProfileView(generics.RetrieveUpdateAPIView):
    """
    GET /business-profile/ -> Retrieve profile (no hours)
    PATCH /business-profile/ -> Update profile only
    """
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticatedAndVerified]
    http_method_names = ['get', 'patch']

    def get_object(self):
        profile, created = BusinessProfile.objects.get_or_create(user=self.request.user)
        return profile


class BusinessHoursViewSet(viewsets.ViewSet):
    """
    Manage business hours separately from profile.
    """
    permission_classes = [IsAuthenticatedAndVerified]
    serializer_class = BusinessHoursSerializer

    def get_queryset(self):
        return BusinessHours.objects.filter(business__user=self.request.user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        business_profile = BusinessProfile.objects.get(user=request.user)
        hours_data = request.data  # Expecting a list of hours objects

        for hour_data in hours_data:
            day = hour_data.get('day')
            BusinessHours.objects.update_or_create(
                business=business_profile,
                day=day,
                defaults={
                    'open_time': hour_data.get('open_time'),
                    'close_time': hour_data.get('close_time'),
                    'is_closed': hour_data.get('is_closed', False),
                }
            )

        return Response({"status": "Business hours updated"}, status=status.HTTP_200_OK)
