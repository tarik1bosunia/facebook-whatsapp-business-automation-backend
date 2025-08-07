# current errors

## when request with message (tomar dokane ki  ki ache)

response is : An error occurred while processing your request.

```plaintext
fbaserver-container     | Last message: content='' additional_kwargs={'function_call': {'name': 'product_search_tool', 'arguments': '{}'}} response_metadata={'prompt_feedback': {'block_reason': 0, 'safety_ratings': []}, 'finish_reason': 'STOP', 'model_name': 'gemini-2.0-flash', 'safety_ratings': []} id='run--1aa64079-0b52-4b92-8ef2-5967536bf367-0' tool_calls=[{'name': 'product_search_tool', 'args': {}, 'id': 'e5aa1357-21e0-4568-8fbf-1ca85c1c8d88', 'type': 'tool_call'}] usage_metadata={'input_tokens': 1312, 'output_tokens': 5, 'total_tokens': 1317, 'input_token_details': {'cache_read': 0}}
fbaserver-container     | ERROR 2025-08-07 01:29:25,845 agent_core Error in agent response generation: 1 validation error for InputSchema
fbaserver-container     |   Value error, At least one search filter (name, category, price, or stock) must be provided. [type=value_error, input_value={}, input_type=dict]                                                                                         
fbaserver-container     |     For further information visit https://errors.pydantic.dev/2.11/v/value_error
fbaserver-container     | ERROR 2025-08-07 01:29:25,845 chat_agent Error in get_response: 1 validation error for InputSchema      
fbaserver-container     |   Value error, At least one search filter (name, category, price, or stock) must be provided. [type=value_error, input_value={}, input_type=dict]    
```
