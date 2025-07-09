from rest_framework.views import exception_handler as drf_exception_handler

def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is not None and isinstance(response.data, dict):
        response.data = {"errors": response.data}

    return response
