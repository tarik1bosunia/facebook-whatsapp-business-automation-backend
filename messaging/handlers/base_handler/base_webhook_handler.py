from abc import ABC, abstractmethod

from django.http import HttpResponseForbidden, HttpRequest, HttpResponse

from business.models.integrations import FacebookIntegration, WhatsAppIntegration
from messaging.exceptions import WebhookVerificationError


class BaseWebHookHandler(ABC):
    def __init__(self):
        # i can get fb_page_id or whatsapp_number_id from messesages when i get post messgage from webhook
        # but the issue is when sent a get request to test the webhook facebook graph api , how can i give him token
        # here need to extract user
        # token will be extract from user
        # self.verify_token = verification_token
        self.user = None


    def handle_webhook(self, request):
        if request.method == 'GET':
            return self._handle_verification(request)
        elif request.method == 'POST':
            return self._handle_incoming_message(request)
        return HttpResponseForbidden()

    def _handle_verification(self, request: HttpRequest) -> HttpResponse:
        """Verify webhook subscription with Meta"""
        try:
            mode = request.GET.get('hub.mode')
            verify_token = request.GET.get('hub.verify_token')
            challenge = request.GET.get('hub.challenge')

            if not all([mode, verify_token, challenge]):
                raise WebhookVerificationError(
                    "Missing verification parameters")

            # to keep sepharate facebook and whatsapp integrations i need to get facebook integrations or whatsapp integrations here by token
            # how can i get it here?

            if 'messenger' in request.path:
                integration = FacebookIntegration.objects.filter(verify_token=verify_token).first()
            elif 'whatsapp' in request.path:
                integration = WhatsAppIntegration.objects.filter(verify_token=verify_token).first()

            if not integration:
                raise WebhookVerificationError("no integration found!")
            
            self.verify_token = integration.verify_token
  

            if mode == 'subscribe' and verify_token == self.verify_token:
                return HttpResponse(
                    challenge,
                    content_type='text/plain',
                    status=200
                )

            raise WebhookVerificationError("Verification token mismatch")

        except WebhookVerificationError as e:
            return HttpResponseForbidden(str(e))
        except Exception as e:
            return HttpResponseForbidden(f"Verification processing failed:: {str(e)}")

    @abstractmethod
    def _handle_incoming_message(self, request):
        """Process the incoming message"""
        raise NotImplementedError(
            "_handle_incoming_message method must be implemented.")
