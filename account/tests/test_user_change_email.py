from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from account.models import PendingEmailChange

User = get_user_model()

class UserChangeEmailTests(APITestCase):
    def setUp(self):
        # User with verified email
        self.verified_user = User.objects.create_user(
            email="verified@example.com",
            password="TestPassword123",
            is_email_verified=True
        )

        # User without verified email
        self.unverified_user = User.objects.create_user(
            email="unverified@example.com",
            password="TestPassword123",
            is_email_verified=False
        )

        self.url = reverse('change-email')  # Replace with your actual url name

    def test_verified_user_can_change_email_successfully(self):
        self.client.force_authenticate(user=self.verified_user)
        data = {
            "password": "TestPassword123",
            "email": "newemail@example.com"
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertIn("detail", response.data)

        # Confirm pending email change created
        pending = PendingEmailChange.objects.filter(
            user=self.verified_user, new_email__iexact="newemail@example.com"
        )
        self.assertTrue(pending.exists())

    def test_unverified_user_cannot_access(self):
        self.client.force_authenticate(user=self.unverified_user)
        data = {
            "password": "TestPassword123",
            "email": "newemail@example.com"
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_access(self):
        self.client.force_authenticate(user=None)
        data = {
            "password": "TestPassword123",
            "email": "newemail@example.com"
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_email_with_wrong_password(self):
        self.client.force_authenticate(user=self.verified_user)
        data = {
            "password": "WrongPassword",
            "email": "newemail@example.com"
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(response.data["password"][0], "Incorrect password.")

    def test_change_email_to_same_email(self):
        self.client.force_authenticate(user=self.verified_user)
        data = {
            "password": "TestPassword123",
            "email": "verified@example.com"  # same as current email
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(
            response.data["email"][0],
            "New email cannot be the same as current email."
        )

    def test_change_email_to_existing_verified_email(self):
        # Another verified user with this email
        User.objects.create_user(
            email="existing@example.com",
            password="OtherPass123",
            is_email_verified=True
        )
        self.client.force_authenticate(user=self.verified_user)
        data = {
            "password": "TestPassword123",
            "email": "existing@example.com"
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"][0], "This email is already in use.")

    def test_change_email_to_pending_email_of_another_user(self):
        other_user = User.objects.create_user(
            email="other@example.com",
            password="OtherPass123",
            is_email_verified=True
        )
        # Create a pending email change for other_user
        PendingEmailChange.create_for_user(
            user=other_user,
            new_email="pending@example.com",
            expiration_hours=24
        )
        self.client.force_authenticate(user=self.verified_user)
        data = {
            "password": "TestPassword123",
            "email": "pending@example.com"
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(
            response.data["email"][0],
            "This email address is currently being verified by another user."
        )
