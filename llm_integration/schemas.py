# apps/llm_integration/api/schemas.py
from drf_spectacular.utils import extend_schema, OpenApiResponse

assistant_schema = extend_schema(
    description="Get AI-generated response to customer messages",
    request={
        'type': 'object',
        'properties': {
            'message': {'type': 'string'}
        }
    },
    responses={
        200: OpenApiResponse(
            description="Successful response",
            examples={
                'application/json': {
                    'response': 'string',
                    'context_used': {
                        'faqs_count': 0,
                        'products_count': 0
                    }
                }
            }
        )
    }
)