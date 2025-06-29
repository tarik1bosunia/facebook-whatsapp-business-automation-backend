import requests
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from messaging.models import ChatMessage

def media_proxy(request):
    media_id = request.GET.get('media_id')
    if not media_id:
        return HttpResponseNotFound("Missing media_id")

    try:
        # Step 1: Get media URL from API
        url = f"https://graph.facebook.com/v23.0/{media_id}"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        media_url = response.json().get('url')

        # Step 2: Download actual media
        media_response = requests.get(media_url, headers=headers, stream=True)
        media_response.raise_for_status()

        content_type = media_response.headers.get('Content-Type', 'application/octet-stream')
        return HttpResponse(media_response.content, content_type=content_type)

    except Exception as e:
        return HttpResponseNotFound(f"Failed to fetch media: {str(e)}")
