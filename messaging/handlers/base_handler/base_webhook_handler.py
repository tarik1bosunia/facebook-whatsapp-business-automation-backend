from abc import ABC, abstractmethod

from django.http import HttpResponseForbidden, HttpRequest, HttpResponse

from messaging.exceptions import WebhookVerificationError


class BaseWebHookHandler(ABC):
    def __init__(self, verification_token):
        self.verify_token = verification_token

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
            token = request.GET.get('hub.verify_token')
            challenge = request.GET.get('hub.challenge')

            if not all([mode, token, challenge]):
                raise WebhookVerificationError("Missing verification parameters")

            if mode == 'subscribe' and token == self.verify_token:
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
        raise NotImplementedError("_handle_incoming_message method must be implemented.")
