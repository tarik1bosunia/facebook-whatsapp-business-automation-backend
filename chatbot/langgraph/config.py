from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, user):
        self.user = user
    
    def get_ai_config(self):
        try:
            config = self.user.ai_config
            if not config.ai_model:
                raise ValueError("AI model not configured")
            return config
        except ObjectDoesNotExist:
            logger.error(f"No AI config for user {self.user.id}")
            raise ValueError("User has no AI configuration")
        except Exception as e:
            logger.error(f"Config error: {str(e)}")
            raise
    
    def validate_initialization(self, conversation=None):
        """Validate required attributes exist"""
        if not hasattr(self.user, 'ai_config'):
            raise ValueError("User model must have ai_config relation")
        if conversation and not hasattr(conversation, 'id'):
            raise ValueError("Conversation must have id field")