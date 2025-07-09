import json
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..models import FacebookIntegration

User = get_user_model()


class FacebookIntegrationViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            is_email_verified=True
        )
        self.url = reverse('facebook-integration')
        self.client.force_authenticate(user=self.user)

    def test_get_configuration(self):
        FacebookIntegration.objects.create(
            user=self.user,
            platform_id='12345',
            access_token='test_token'
        )
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['platform_id'], '12345')
        self.assertNotIn('access_token', response.data)

    def test_create_with_missing_fields(self):
        response = self.client.put(self.url, {'is_connected': True})
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.content)

        self.assertIn("errors", data)
        self.assertIn('platform_id', data['errors'])
