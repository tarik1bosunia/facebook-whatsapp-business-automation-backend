from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.utils import timezone

from account.models import PendingEmailChange
from account.renderers import UserRenderer

from account.serializers import UserChangeEmailSerializer


class UserChangeEmailView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserChangeEmailSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Verification email sent to new address',
                'detail': 'Please check your new email to complete the change'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailChangeView(APIView):
    def get(self, request, token):
        try:
            pending_change = PendingEmailChange.objects.get(
                token=token,
                expires_at__gte=timezone.now()
            )
            user = pending_change.user
            user.email = pending_change.new_email
            user.save()
            pending_change.delete()
            return Response({'message': 'Email successfully updated'}, status=status.HTTP_200_OK)
        except PendingEmailChange.DoesNotExist:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)