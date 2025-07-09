from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class TestUserChangePassword(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='OldPassword123',
            is_email_verified=True,
            is_active=True,
        )
        self.url = reverse('change-password')  # 🔁 Adjust this if needed

    def get_auth_headers(self, user=None):
        if not user:
            user = self.user
        refresh = RefreshToken.for_user(user)
        return {
            'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'
        }

    def test_password_change_success(self):
        headers = self.get_auth_headers()
        response = self.client.post(self.url, {
            'old_password': 'OldPassword123',
            'new_password': 'NewPassword456'
        }, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword456'))

    def test_password_change_with_wrong_old_password(self):
        headers = self.get_auth_headers()
        response = self.client.post(self.url, {
            'old_password': 'WrongPassword',
            'new_password': 'NewPassword456'
        }, **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)

    def test_password_change_with_same_old_new_password(self):
        headers = self.get_auth_headers()
        response = self.client.post(self.url, {
            'old_password': 'OldPassword123',
            'new_password': 'OldPassword123'
        }, **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password', response.data)

    def test_password_change_requires_authentication(self):
        response = self.client.post(self.url, {
            'old_password': 'OldPassword123',
            'new_password': 'NewPassword456'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unverified_email_cannot_change_password(self):
        self.user.is_email_verified = False
        self.user.save()
        headers = self.get_auth_headers()
        response = self.client.post(self.url, {
            'old_password': 'OldPassword123',
            'new_password': 'NewPassword456'
        }, **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_password_change_with_too_short_password(self):
        headers = self.get_auth_headers()
        response = self.client.post(self.url, {
            'old_password': 'OldPassword123',
            'new_password': 'short'  # Less than 8 characters
        }, **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password', response.data)
        self.assertEqual(
            response.data['new_password'][0],
            'Password must be at least 8 characters long.'
        )

    def test_password_change_with_minimum_length_password(self):
        headers = self.get_auth_headers()
        response = self.client.post(self.url, {
            'old_password': 'OldPassword123',
            'new_password': 'Exactly8'  # Exactly 8 characters
        }, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Exactly8'))