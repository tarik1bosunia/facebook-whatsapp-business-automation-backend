import json
import logging
from business.models import BusinessProfile

logger = logging.getLogger(__name__)

class BusinessTool:
    def __init__(self, user):
        self.user = user

    def get_info(self) -> str:
        """Get business profile information"""
        try:
            business = BusinessProfile.objects.get(user=self.user)
            return json.dumps({
                'name': business.name,
                'email': business.email,
                'phone': business.phone
            })
        except Exception as e:
            logger.error(f"Business info failed: {str(e)}")
            return json.dumps({"error": "Business info unavailable"})