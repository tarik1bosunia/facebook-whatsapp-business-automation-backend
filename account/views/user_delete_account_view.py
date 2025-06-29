from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from account.renderers import UserRenderer
from account.serializers import UserDeleteAccountSerializer


class UserDeleteAccountView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        serializer = UserDeleteAccountSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.delete()
            return Response({'message': 'Account deleted successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)