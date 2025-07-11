from rest_framework.renderers import JSONRenderer
import json
from rest_framework.exceptions import ErrorDetail
from collections import OrderedDict
from django.core.serializers.json import DjangoJSONEncoder 


class CustomRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            return b''

        response_dict = {}
        if isinstance(data, dict):
            # Handle validation errors
            if any(
                isinstance(value, (ErrorDetail, list)) or 
                (isinstance(value, dict) and any(isinstance(v, (ErrorDetail, list)) for v in value.values()))
                for value in data.values()
            ):
                # Convert single error strings to list format
                errors = OrderedDict()
                for key, value in data.items():
                    if isinstance(value, ErrorDetail):
                        errors[key] = [str(value)]
                    elif isinstance(value, list):
                        errors[key] = [str(v) if isinstance(v, ErrorDetail) else v for v in value]
                    elif isinstance(value, dict):
                        # Handle nested errors
                        nested_errors = OrderedDict()
                        for k, v in value.items():
                            if isinstance(v, ErrorDetail):
                                nested_errors[k] = [str(v)]
                            elif isinstance(v, list):
                                nested_errors[k] = [str(item) if isinstance(item, ErrorDetail) else item for item in v]
                            else:
                                nested_errors[k] = v
                        errors[key] = nested_errors
                    else:
                        errors[key] = value
                response_dict['errors'] = errors
            else:
                response_dict = data
        else:
            response_dict = data

        return json.dumps(response_dict, ensure_ascii=False, cls=DjangoJSONEncoder).encode(self.charset)
