from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from account.models import PendingEmailChange
from django.contrib.auth import get_user_model

User = get_user_model()


class VerifyEmailChangeViewTests(APITestCase):
    """
    Successful verification with a valid token
    Failure with an invalid token
    Failure with an expired token
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email="old@example.com",
            password="TestPassword123",
            is_email_verified=True
        )
        self.new_email = "new@example.com"
        # Create a valid pending email change with future expiration
        self.pending_change = PendingEmailChange.create_for_user(
            user=self.user,
            new_email=self.new_email,
            expiration_hours=24
        )
        self.valid_token = self.pending_change.token

        self.url = reverse('verify-email-change',
                           kwargs={'token': self.valid_token})

    def test_verify_email_change_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'],
                         "Email successfully updated")

        # Refresh user from db and check email updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.new_email)

        # Check that pending change is deleted
        exists = PendingEmailChange.objects.filter(
            pk=self.pending_change.pk).exists()
        self.assertFalse(exists)

    def test_verify_email_change_invalid_token(self):
        invalid_url = reverse('verify-email-change',
                              kwargs={'token': 'invalidtoken123'})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Invalid or expired token")

    def test_verify_email_change_expired_token(self):
        # Expire the token manually
        self.pending_change.expires_at = timezone.now() - timezone.timedelta(hours=1)
        self.pending_change.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Invalid or expired token")

        # Email should not have changed
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, self.new_email)
        self.assertEqual(self.user.email, "old@example.com")
