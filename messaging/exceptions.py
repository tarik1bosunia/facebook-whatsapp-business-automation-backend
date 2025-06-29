class WebhookVerificationError(Exception):
    """Raised when webhook verification fails"""
    pass

class FacebookAPIError(Exception):
    """Raised when Facebook API calls fail"""
    pass

class MessageProcessingError(Exception):
    """Raised when message processing fails"""
    pass