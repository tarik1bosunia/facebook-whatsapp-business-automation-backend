from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class UserDeleteAccountTests(APITestCase):
    """
    ✅ Authenticated user deletes their own account

    ❌ Incorrect password

    ❌ Non-existent email

    ❌ Missing fields

    ❌ Authenticated user tries to delete another account

    ❌ Unauthenticated user tries to delete
    """
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='UserPass123',
            is_email_verified=True
        )
        self.another_user = User.objects.create_user(
            email='other@example.com',
            password='OtherPass123',
            is_email_verified=True
        )
        self.url = reverse('delete-account')

    def test_authenticated_user_can_delete_self(self):
        self.client.force_authenticate(user=self.user)

        payload = {
            "email": self.user.email,
            "password": "UserPass123"
        }
        response = self.client.delete(self.url, data=payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Account deleted successfully")
        self.assertFalse(User.objects.filter(email=self.user.email).exists())

    def test_delete_account_with_wrong_password(self):
        self.client.force_authenticate(user=self.user)

        payload = {
            "email": self.user.email,
            "password": "WrongPassword"
        }
        response = self.client.delete(self.url, data=payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_delete_account_with_nonexistent_email(self):
        self.client.force_authenticate(user=self.user)

        payload = {
            "email": "notfound@example.com",
            "password": "SomePass123"
        }
        response = self.client.delete(self.url, data=payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_delete_account_missing_fields(self):
        self.client.force_authenticate(user=self.user)

        payload = {}  # no email, no password
        response = self.client.delete(self.url, data=payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_delete_other_user(self):
        self.client.force_authenticate(user=self.user)

        payload = {
            "email": self.another_user.email,
            "password": "OtherPass123"
        }
        response = self.client.delete(self.url, data=payload)

        # The serializer will validate the credentials, so this test will actually pass unless extra logic is added
        # If you want to restrict deletion to only self, you must add that check in `validate` or `delete` view.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_user_cannot_delete(self):
        payload = {
            "email": self.user.email,
            "password": "UserPass123"
        }
        response = self.client.delete(self.url, data=payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
