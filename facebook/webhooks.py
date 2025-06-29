import json
import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from facebook.handlers import handle_message

@csrf_exempt
def webhook(request):
    if request.method == 'GET':
        # Facebook verification
        verify_token = request.GET.get('hub.verify_token')
        if verify_token == settings.FACEBOOK_VERIFY_TOKEN:
            return HttpResponse(request.GET.get('hub.challenge'))
        return HttpResponse('Invalid verification token', status=403)
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        if data.get('object') == 'page':
            for entry in data.get('entry', []):
                for messaging_event in entry.get('messaging', []):
                    if messaging_event.get('message'):
                        handle_message(messaging_event)
        return HttpResponse('EVENT_RECEIVED', status=200)
    
    return HttpResponse('Invalid request', status=400)