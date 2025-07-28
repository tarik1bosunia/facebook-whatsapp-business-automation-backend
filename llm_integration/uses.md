
```sh
from services.llm_service import LLMService

# Initialize with a user object
llm_service = LLMService(user=request.user)  # or any user object

# Generate a response to a customer message
response = await llm_service.generate_response_async("What time do you open tomorrow?")
```

# Django View (Async)
```sh
from django.http import JsonResponse
from services.llm_service import LLMService

async def chat_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')
        
        llm_service = LLMService(user=request.user)
        response = await llm_service.generate_response_async(message)
        
        return JsonResponse(response)
```

# Django View (Sync - using sync_to_async)
```
from django.http import JsonResponse
from asgiref.sync import sync_to_async
from services.llm_service import LLMService

def chat_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')
        
        llm_service = LLMService(user=request.user)
        response = sync_to_async(llm_service.generate_response_async)(message)
        
        return JsonResponse(response)

```