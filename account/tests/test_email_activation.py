from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

class ActivateUserEmailViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='Password123!',
            is_email_verified=False,
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.activation_url = reverse('activate-user-email', kwargs={'uid': self.uid, 'token': self.token})

    def test_activate_user_email_success(self):
        response = self.client.get(self.activation_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Email successfully verified')

        # Refresh user from DB to check is_email_verified
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_activate_user_email_invalid_token(self):
        invalid_token_url = reverse('activate-user-email', kwargs={'uid': self.uid, 'token': 'invalid-token'})
        response = self.client.get(invalid_token_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid activation link')

    def test_activate_user_email_invalid_uid(self):
        invalid_uid = urlsafe_base64_encode(force_bytes(99999))  # Assuming no user with this ID
        invalid_uid_url = reverse('activate-user-email', kwargs={'uid': invalid_uid, 'token': self.token})
        response = self.client.get(invalid_uid_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid activation link')
