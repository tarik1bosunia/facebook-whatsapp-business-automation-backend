from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import FacebookIntegration, WhatsAppIntegration
from django.core.exceptions import ValidationError

User = get_user_model()

class PlatformIntegrationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpass123')

    def test_facebook_integration_creation(self):
        integration = FacebookIntegration.objects.create(
            user=self.user,
            platform_id='12345',
            access_token='test_token',
            verify_token='test_verify'
        )
        self.assertEqual(str(integration), "Facebook Integration: 12345 (User: test@example.com)")

    def test_validation_when_connected(self):
        integration = FacebookIntegration(
            user=self.user,
            is_connected=True
        )
        with self.assertRaises(ValidationError):
            integration.full_clean()