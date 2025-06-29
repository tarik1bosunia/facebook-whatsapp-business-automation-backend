# messaging/views/conversation.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from messaging.models.conversation import Conversation
from messaging.serializers import AutoReplySerializer
from django.shortcuts import get_object_or_404

class AutoReplyToggleView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def patch(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk)
        serializer = AutoReplySerializer(conversation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
