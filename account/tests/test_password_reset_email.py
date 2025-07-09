from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
import json

User = get_user_model()

class SendPasswordResetEmailViewTest(APITestCase):
    """
    Sending password reset for a registered and active user triggers email sending

    Sending password reset for a non-existent or inactive user does not trigger email sending but still returns success message (to avoid leaking info)

    Validation errors (like missing or invalid email)
    """
    def setUp(self):
        self.url = reverse('send-password-reset-email')
        self.user_email = 'activeuser@example.com'
        self.user_password = 'StrongPassword123'
        self.user = User.objects.create_user(
            email=self.user_email,
            password=self.user_password,
            is_active=True
        )
        self.inactive_user = User.objects.create_user(
            email='inactive@example.com',
            password='AnyPass123',
            is_active=False
        )

    @patch('account.utils.Util.send_email')
    @patch('account.utils.Util.get_frontend_base_url')
    def test_send_password_reset_email_active_user(self, mock_get_frontend_base_url, mock_send_email):
        mock_get_frontend_base_url.return_value = 'http://frontend.test'

        payload = {'email': self.user_email}
        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('msg', response.data)
        self.assertEqual(response.data['msg'], 'If this email is registered, you will receive a password reset link shortly.')
        mock_send_email.assert_called_once()

        # Check email_data passed to send_email
        email_data = mock_send_email.call_args[0][0]
        self.assertEqual(email_data['to_email'], self.user_email)
        self.assertIn('Reset Your Password', email_data['subject'])
        self.assertIn('http://frontend.test/reset-password/', email_data['body'])

    @patch('account.utils.Util.send_email')
    def test_send_password_reset_email_inactive_user(self, mock_send_email):
        payload = {'email': 'inactive@example.com'}
        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('msg', response.data)
        self.assertFalse(mock_send_email.called)  # Email not sent for inactive user

    @patch('account.utils.Util.send_email')
    def test_send_password_reset_email_nonexistent_user(self, mock_send_email):
        payload = {'email': 'notfound@example.com'}
        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('msg', response.data)
        self.assertFalse(mock_send_email.called)  # Email not sent because user doesn't exist

    def test_send_password_reset_email_invalid_email(self):
        payload = {'email': 'invalid-email'}
        response = self.client.post(self.url, payload, format='json')
        data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", data)
        self.assertIn("email", data["errors"])
