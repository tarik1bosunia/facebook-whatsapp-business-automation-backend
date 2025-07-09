from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

class UserRegistrationEmailVerificationTest(APITestCase):
    """
    Mocks the email sending logic so no actual email is sent.

    Verifies that the activation link was built and contains valid data.

    Decodes the UID and validates the Django token manually.

    Ensures that registration includes all necessary steps for email verification.
    """
    def setUp(self):
        self.registration_url = reverse('registration')
        self.payload = {
            "email": "verifyme@example.com",
            "first_name": "Verify",
            "last_name": "Me",
            "password": "SecurePass123"
        }

    @patch('account.utils.Util.send_email')
    def test_registration_sends_verification_email(self, mock_send_email):
        response = self.client.post(self.registration_url, self.payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(mock_send_email.called)

        # Get the email arguments
        email_data = mock_send_email.call_args[0][0]
        self.assertIn("to_email", email_data)
        self.assertEqual(email_data["to_email"], self.payload["email"])
        self.assertIn("Click to verify your email", email_data["body"])

        # Extract uid and token from the link
        import re
        match = re.search(r'/activate/(?P<uid>[^/]+)/(?P<token>[^/]+)/', email_data['body'])
        self.assertIsNotNone(match)

        uid = match.group("uid")
        token = match.group("token")

        # Validate UID and token manually
        decoded_uid = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=decoded_uid)
        self.assertTrue(default_token_generator.check_token(user, token))
