from django.utils.deprecation import MiddlewareMixin
from .langchain import LLMResponseGenerator
import json
from .models import AIConfiguration

class AutoResponseMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Skip if not a chat-related response or auto-respond is disabled
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response
        
        try:
            ai_config = AIConfiguration.objects.get(user=request.user)
            if not ai_config.auto_respond:
                return response
            
            # Check if this is a chat message that needs a response
            if self._needs_auto_response(request, response):
                user_message = self._extract_user_message(request)
                generator = LLMResponseGenerator(ai_config)
                ai_response = generator.generate_response(user_message)
                
                # Modify the response to include AI response
                if hasattr(response, 'data'):
                    response.data['ai_response'] = ai_response
                else:
                    # Handle other response types as needed
                    pass
                
        except AIConfiguration.DoesNotExist:
            pass
        
        return response
    
    def _needs_auto_response(self, request, response):
        """Determine if this request/response pair needs an auto-response"""
        # Implement your logic here based on your URL patterns or content
        return request.path.startswith('/chat/') and request.method == 'POST'
    
    def _extract_user_message(self, request):
        """Extract the user message from the request"""
        # Implement based on how your frontend sends data
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                return data.get('message', '')
            except json.JSONDecodeError:
                return ''
        return request.POST.get('message', '')