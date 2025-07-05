from django.http import JsonResponse
from django.conf import settings
from django.middleware.common import CommonMiddleware

class TrailingSlashMiddleware(CommonMiddleware):
    def process_request(self, request):
        try:
            return super().process_request(request)
        except RuntimeError as e:
            if (
                request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and
                "You called this URL via" in str(e) and
                settings.APPEND_SLASH
            ):
                return JsonResponse({
                    "detail": "Trailing slash missing. Please add a trailing slash to the URL."
                }, status=400)
            raise
