import requests
from django.conf import settings
from ..exceptions import FacebookAPIError

def send_message(recipient_id, text):
    url = "https://graph.facebook.com/v22.0/me/messages"
    
    try:
        response = requests.post(
            url,
            params={"access_token": settings.FB_PAGE_ACCESS_TOKEN},
            headers={"Content-Type": "application/json"},
            json={
                "recipient": {"id": recipient_id},
                "message": {"text": text}
            }
        )
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        raise FacebookAPIError(f"Facebook API error: {str(e)}")