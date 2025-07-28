import json
import logging
from knowledge_base.models import FAQ

logger = logging.getLogger(__name__)

class FAQTool:
    def __init__(self, user):
        self.user = user

    def search(self, query: str) -> str:
        """Search FAQ entries"""
        try:
            faqs = FAQ.objects.filter(
                category__user=self.user
            )[:3].values('question', 'answer')
            return json.dumps(list(faqs))
        except Exception as e:
            logger.error(f"FAQ search failed: {str(e)}")
            return json.dumps({"error": "FAQ search unavailable"})