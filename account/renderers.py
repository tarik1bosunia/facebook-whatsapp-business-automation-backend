from rest_framework.renderers import JSONRenderer
import json
from rest_framework.exceptions import ErrorDetail


class UserRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = ''

        if data is not None and isinstance(data, dict):
            if any(isinstance(v[0], ErrorDetail) for v in data.values() if isinstance(v, list)):
                response = json.dumps({'errors': data})
            else:
                response = json.dumps(data)
        else:
            response = json.dumps(data)

        return response