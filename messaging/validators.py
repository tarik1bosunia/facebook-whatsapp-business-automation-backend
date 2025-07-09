from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
import re
from urllib.parse import urlparse

class MessageValidator:
    """Validator for chat message content"""
    
    MAX_LENGTH = 2000  # characters
    MAX_URLS = 5  # maximum URLs allowed in a message
    BLACKLISTED_PATTERNS = [
        r'<script.*?>.*?</script>',  # script tags
        r'on\w+=".*?"',  # HTML event handlers
        r'javascript:',  # javascript protocol
    ]
    
    @classmethod
    def validate_content(cls, content: str) -> bool:
        """
        Validate message content for:
        - Length
        - HTML/JS injection
        - URL count
        - Blacklisted patterns
        """
        if not content or not isinstance(content, str):
            raise ValidationError("Message content must be a non-empty string")
        
        content = content.strip()
        
        # Check length
        if len(content) > cls.MAX_LENGTH:
            raise ValidationError(f"Message too long (max {cls.MAX_LENGTH} characters)")
        
        # Check for HTML/JS injection
        sanitized = strip_tags(content)
        if sanitized != content:
            raise ValidationError("HTML tags are not allowed in messages")
        
        # Check for blacklisted patterns
        for pattern in cls.BLACKLISTED_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                raise ValidationError("Message contains disallowed content")
        
        # Check URL count
        urls = cls.extract_urls(content)
        if len(urls) > cls.MAX_URLS:
            raise ValidationError(f"Too many URLs (max {cls.MAX_URLS} allowed)")
        
        return True
    
    @staticmethod
    def extract_urls(text: str) -> list:
        """Extract all URLs from text"""
        # This simple regex matches most common URL patterns
        url_pattern = r'(https?://[^\s]+)'
        urls = re.findall(url_pattern, text)
        
        # Validate the found URLs
        valid_urls = []
        for url in urls:
            try:
                result = urlparse(url)
                if all([result.scheme, result.netloc]):
                    valid_urls.append(url)
            except ValueError:
                continue
                
        return valid_urls


def validate_message_content(content: str):
    """Public interface for message validation"""
    return MessageValidator.validate_content(content)