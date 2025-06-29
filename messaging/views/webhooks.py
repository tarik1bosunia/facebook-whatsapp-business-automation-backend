from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, HttpResponse

from messaging.handlers import MessengerHandler, WhatsAppHandler


def webhook_view(handler_class):
    @csrf_exempt
    def view(request: HttpRequest) -> HttpResponse:
        handler = handler_class()
        return handler.handle_webhook(request)
    return view

messenger_webhook = webhook_view(MessengerHandler)
whatsapp_webhook = webhook_view(WhatsAppHandler)
