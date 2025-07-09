from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserLogoutViewTests(APITestCase):
    """
    Successful logout (token blacklisted)

    Missing refresh token

    Invalid/expired/malformed token

    Unauthenticated access (no token in header)
    """
    def setUp(self):
        self.user = User.objects.create_user(
            email="logoutuser@example.com",
            password="TestPass123!",
            is_email_verified=True
        )
        self.refresh = str(RefreshToken.for_user(self.user))
        self.access = str(RefreshToken.for_user(self.user).access_token)

        self.logout_url = reverse('logout')

    def test_logout_successful(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        response = self.client.post(self.logout_url, data={"refresh": self.refresh})

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(response.data['message'], "Logout successful. Token blacklisted.")

    def test_logout_without_refresh_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        response = self.client.post(self.logout_url, data={})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('refresh', response.data['errors'])

    def test_logout_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        response = self.client.post(self.logout_url, data={"refresh": "invalid_token"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_erros', response.data['errors'])

    def test_logout_unauthenticated(self):
        # No credentials set
        response = self.client.post(self.logout_url, data={"refresh": self.refresh})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
