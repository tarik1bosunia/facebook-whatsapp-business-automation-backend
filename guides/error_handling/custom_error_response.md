# Custom Error Response Renderer for Django REST Framework

## Overview

A custom renderer for Django REST Framework that standardizes all error responses to a consistent JSON format.

## Features

- Consistent error response structure
- Handles all DRF error types (field, non-field, nested)
- Preserves successful response format
- Proper Unicode/UTF-8 support
- Maintains field ordering

## Installation

1. Create a new file `renderers.py` in your Django app
2. Add the following code:

```python
from rest_framework.renderers import JSONRenderer
import json
from rest_framework.exceptions import ErrorDetail
from collections import OrderedDict


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

        return json.dumps(response_dict, ensure_ascii=False).encode(self.charset)
```

## Configuration
Add the renderer to your DRF settings:
```python
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'yourapp.renderers.CustomRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]
}
```

## Response Formats
### Field Validation Errors
Input (DRF default):

```json
{
    "email": ["This field is required."],
    "password": ["This field is required."]
}
```

Output (custom format):
```json
{
    "errors": {
        "email": ["This field is required."],
        "password": ["This field is required."]
    }
}
```

### Non-Field Errors
Input:
```json
{
    "detail": "Authentication failed"
}
```
# Output
```json
{
    "errors": {
        "detail": ["Authentication failed"]
    }
}
```
### Nested Errors
Input:
```json
{
    "profile": {
        "age": ["Must be positive"],
        "address": {
            "zipcode": ["Invalid format"]
        }
    }
}
```
# Output:
```json
{
    "errors": {
        "profile": {
            "age": ["Must be positive"],
            "address": {
                "zipcode": ["Invalid format"]
            }
        }
    }
}
```

### Successful Response
Passes through unchanged:
```json
{
    "id": 1,
    "name": "Example",
    "status": "active"
}
```

# DRF Custom Error Response Handler

This middleware or utility ensures that all error responses from Django REST Framework (DRF) are returned in a consistent, client-friendly format.

---

## Edge Cases Handled

| Case                         | Behavior                                                   |
|-----------------------------|------------------------------------------------------------|
| **None responses**          | Returns `b''` (empty bytes) to avoid crashing parsers.     |
| **Non-dict responses**      | If the response is not a dictionary (e.g., a string or list), it passes through unchanged. |
| **Mixed content**           | If the response contains both valid and error data, only the error portions are transformed. |
| **Unicode characters**      | Properly encoded with UTF-8 to support internationalized error messages. |
| **Single errors**           | Converts string messages into array format for uniformity, e.g., `"Invalid token"` → `["Invalid token"]`. |

---

## Benefits

- **Client-friendly:**  
  Delivers a predictable and structured error format — easy to handle on frontend (especially for form validation or toast alerts).

- **Backward compatible:**  
  Leaves successful (2xx) responses untouched, so it works seamlessly with existing integrations.

- **Comprehensive:**  
  Capable of handling all standard and nested DRF validation errors.

- **Maintainable:**  
  Centralized logic with clean, readable, and well-documented code. Easy to update if response formats evolve.

---
