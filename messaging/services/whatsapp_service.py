import requests
import logging
from django.conf import settings
from requests.exceptions import RequestException
import re
import httpx

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.base_url = f"{settings.WHATSAPP_API_BASE_URL}/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}"

    def _send_request(self, endpoint, payload):
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=10  # 10 seconds timeout
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"WhatsApp API Error: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"API Response: {e.response.text}")
            raise

    def send_text_message(self, phone_number, message):
        if not re.match(r'^\d{10,15}$', phone_number):  # Basic validation
            raise ValueError("Invalid phone number format")
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {"body": message},
        }
        return self._send_request("messages", payload)

    async def send_text_message_async(self, phone_number, message):
        async with httpx.AsyncClient() as client:
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {"body": message},
            }
            response = await client.post(
                f"{self.base_url}/messages",
                headers={"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"},
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()

    def send_image(self, phone_number, image_url, caption=None):
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "image",
            "image": {"link": image_url, "caption": caption},
        }
        return self._send_request("messages", payload)

    def send_template(self, phone_number, template_name, language_code="en", components=None):
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
            },
        }
        if components:
            payload["template"]["components"] = components
        return self._send_request("messages", payload)