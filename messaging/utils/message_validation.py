import logging
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

def validate_message_content(content: str):
    """
    Validates the content of a message.
    Raises ValidationError if content is invalid.
    """
    if not isinstance(content, str):
        logger.error("Message content must be a string.")
        raise ValidationError("Message content must be a string.")
    if not content.strip():
        logger.error("Message content cannot be empty.")
        raise ValidationError("Message content cannot be empty.")
    # Add more validation rules as needed