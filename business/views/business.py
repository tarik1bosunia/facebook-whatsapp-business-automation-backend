# views.py
from rest_framework import viewsets, permissions, status, generics, filters
from business.models import BusinessProfile, BusinessHours
from ..serializers import BusinessProfileSerializer, BusinessHoursSerializer
from rest_framework.response import Response

from rest_framework.exceptions import ValidationError

class BusinessProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = BusinessProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        try:
            return user.business
        except BusinessProfile.DoesNotExist:
            return None
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance, data=request.data)
        else:
            serializer = self.get_serializer(data={**request.data, 'user': request.user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)

    # def retrieve(self, request):
    #     profile = self.get_object()
    #     if not profile:
    #         return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    #     serializer = BusinessProfileSerializer(profile)
    #     return Response(serializer.data)
    


    # def create(self, request):
    #     if self.get_object():
    #         return Response({'detail': 'Profile already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    #     serializer = BusinessProfileSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(user=request.user)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def update(self, request):
    #     profile = self.get_object()
    #     if not profile:
    #         return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    #     serializer = BusinessProfileSerializer(profile, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data)


class BusinessHoursViewSet(viewsets.ModelViewSet):
    serializer_class = BusinessHoursSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    

    def get_queryset(self):
        return BusinessHours.objects.filter(business__user=self.request.user)

    def perform_create(self, serializer):
        business = BusinessProfile.objects.get(user=self.request.user)
        day = serializer.validated_data['day']
        instance, created = BusinessHours.objects.update_or_create(
            business=business,
            day=day,
            defaults={
                'open_time': serializer.validated_data.get('open_time'),
                'close_time': serializer.validated_data.get('close_time'),
                'is_closed': serializer.validated_data.get('is_closed', False),
            }
        )
        serializer.instance = instance

    # DEBUG
    # def create(self, request, *args, **kwargs):
    #     print("🔍 Incoming data to create():", request.data)
    #     return super().create(request, *args, **kwargs)

    # def update(self, request, *args, **kwargs):
    #     print("🔍 Incoming data to update():", request.data)
    #     return super().update(request, *args, **kwargs)    









