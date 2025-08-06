import requests
from django.conf import settings
from ..exceptions import FacebookAPIError

def send_message(recipient_id, text, access_token):
    url = "https://graph.facebook.com/v23.0/me/messages"
    
    try:
        response = requests.post(
            url,
            params={"access_token": access_token},
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