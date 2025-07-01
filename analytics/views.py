from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services.analytics_service import AnalyticsService

class ConversationAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        stats = AnalyticsService.get_conversation_stats(request.user)
        return Response({
            'value': f"{stats['total']:,}",
            'change': stats['change'],
            'trend': stats['trend']
        })