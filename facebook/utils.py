import requests
import json
from django.conf import settings

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={settings.FACEBOOK_PAGE_ACCESS_TOKEN}"
    
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
        "messaging_type": "RESPONSE"
    }
    
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(
        url,
        data=json.dumps(payload),
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")
    
    return response.json()