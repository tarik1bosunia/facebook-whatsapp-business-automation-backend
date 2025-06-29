import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework import viewsets
from account.renderers import UserRenderer
from chatbot.services.llm.agents import ChatAgent
from chatbot.utils import ChatBotUtil
from account.permissions import IsSuperAdminOrReadOnlyBusinessman


# Initialize the OpenAI client
@csrf_exempt
def chat_with_ai(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            prompt = data.get("prompt")

            if not prompt:
                return JsonResponse({"error": "Prompt is required."}, status=400)

            # Create chat completion
            response = ChatBotUtil.chat_with_gemini(prompt)
            
            print(response.text)

            return JsonResponse({"response": response.text}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST method allowed"}, status=405)



from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from .models import AIConfiguration, AIModel
from .serializers import AIConfigurationSerializer, AIModelSerializer

class AIConfigurationView(generics.RetrieveUpdateAPIView):
    serializer_class = AIConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Ensure configuration exists for the user
        config, created = AIConfiguration.objects.get_or_create(user=self.request.user)
        return config

    def put(self, request, *args, **kwargs):
        """Allow full updates (overwrites all fields except timestamps/user)"""
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """Allow partial updates (single field or a few)"""
        return self.partial_update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Return the current AI configuration (excluding API key)"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=HTTP_200_OK)



class AIModelViewSet(viewsets.ModelViewSet):
    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer
    permission_classes = [IsSuperAdminOrReadOnlyBusinessman]
    pagination_class = None
    renderer_classes = [UserRenderer]

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import AIConfiguration
from .langchain import LLMResponseGenerator

class ChatMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            message = request.data.get('message')
            # chat_history = request.data.get('history', [])

            if not message:
                return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
            

             # Get AI response
            agent = ChatAgent(request.user)
            ai_response = agent.get_response(message)

            # Get or create AI config
            # ai_config, _ = AIConfiguration.objects.get_or_create(user=request.user)

            # if not ai_config.auto_respond:
            #     return Response({'response': '', 'status': 'auto-respond-disabled'}, status=status.HTTP_200_OK)

            # # Generate response
            # generator = LLMResponseGenerator(ai_config)
            # response = generator.generate_response(user_input, chat_history)

            return Response({'response': ai_response, 'status': 'success'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e), 'status': 'error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


