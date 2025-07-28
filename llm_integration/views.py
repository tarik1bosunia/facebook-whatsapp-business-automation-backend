# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from services.llm_service import LLMService

class CustomerSupportView(APIView):
    """
    API endpoint for customer support interactions with Gemini.
    """
    permission_classes = [IsAuthenticated]
    
    async def post(self, request):
        customer_message = request.data.get('message', '').strip()
        if not customer_message:
            return Response(
                {'error': 'Message is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            llm_service = LLMService(request.user)
            response = await llm_service.generate_response_async(customer_message)
            return Response(response)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



# apps/llm_integration/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..services.gemini_service import GeminiService

class LLMAssistantAPI(APIView):
    def post(self, request):
        message = request.data.get('message', '').strip()
        if not message:
            return Response(
                {'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = GeminiService(request.user)
        response = asyncio.run(service.generate_response(message))
        return Response(response)