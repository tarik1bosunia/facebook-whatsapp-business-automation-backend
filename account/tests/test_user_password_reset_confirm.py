import uuid
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.cache import cache
from django.test import override_settings

User = get_user_model()

@override_settings(REST_FRAMEWORK={
    'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.ScopedRateThrottle'],
    'DEFAULT_THROTTLE_RATES': {'password_reset_confirm': '3/minute'},
})
class PasswordResetConfirmAPITests(APITestCase):

    def setUp(self):
        cache.clear()  # Clear throttle cache before each test

        unique_email = f'testuser_{uuid.uuid4().hex[:6]}@example.com'
        self.user = User.objects.create_user(
            email=unique_email,
            password='oldpassword123',
            is_email_verified=True
        )
        self.valid_uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.valid_token = PasswordResetTokenGenerator().make_token(self.user)
        self.valid_url = reverse('password-reset-confirm', args=[self.valid_uid, self.valid_token])
        self.valid_data = {
            'password': 'NewSecurePassword123!',
            'confirm_password': 'NewSecurePassword123!'
        }

    def test_successful_password_reset(self):
        response = self.client.post(self.valid_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('msg'),
            'Password reset successfully. You can now login with your new password.'
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.valid_data['password']))

    def test_missing_uid_returns_bad_request(self):
        url = reverse('password-reset-confirm', args=['null', self.valid_token])
        response = self.client.post(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Reset token missing in URL.')

    def test_missing_token_returns_bad_request(self):
        url = reverse('password-reset-confirm', args=[self.valid_uid, 'null'])
        response = self.client.post(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Reset token missing in URL.')

    def test_password_mismatch_returns_error(self):
        invalid_data = {
            'password': 'NewPassword123!',
            'confirm_password': 'DifferentPassword123!'
        }
        response = self.client.post(self.valid_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)
        self.assertIn('Passwords do not match.', response.data['confirm_password'])

    def test_weak_password_returns_validation_error(self):
        weak_data = {
            'password': '123',
            'confirm_password': '123'
        }
        response = self.client.post(self.valid_url, weak_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_invalid_uid_returns_error(self):
        response = self.client.post(
            reverse('password-reset-confirm', args=['invaliduid', self.valid_token]),
            self.valid_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response.data)
        self.assertIn('Invalid or expired reset link.', str(response.data['token'][0]))

    def test_invalid_token_returns_error(self):
        response = self.client.post(
            reverse('password-reset-confirm', args=[self.valid_uid, 'invalidtoken']),
            self.valid_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response.data)
        self.assertIn('Invalid or expired reset link.', str(response.data['token'][0]))

    def test_expired_token_returns_error(self):
        self.user.set_password('newpassword')
        self.user.last_password_change = timezone.now()
        self.user.save()

        response = self.client.post(self.valid_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response.data)
        self.assertIn('expired reset link', str(response.data['token'][0]).lower())

    def test_unverified_user_returns_error(self):
        unverified_user = User.objects.create_user(
            email=f'unverified_{uuid.uuid4().hex[:6]}@example.com',
            password='test123',
            is_email_verified=False
        )
        uid = urlsafe_base64_encode(force_bytes(unverified_user.pk))
        token = PasswordResetTokenGenerator().make_token(unverified_user)
        url = reverse('password-reset-confirm', args=[uid, token])

        response = self.client.post(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response.data)
        self.assertIn('expired reset link', str(response.data['token'][0]).lower())

    def test_empty_request_data_returns_error(self):
        response = self.client.post(self.valid_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertIn('confirm_password', response.data)

    def test_throttling_for_password_reset_confirm(self):
        # 3 allowed requests with same token and same user
        for i in range(3):
            response = self.client.post(self.valid_url, self.valid_data)
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
            if response.status_code == status.HTTP_200_OK:
                # Refresh token and URL, as previous token is now invalid
                self.user.set_password('anotherpass')
                self.user.last_password_change = timezone.now()
                self.user.save()
                self.valid_token = PasswordResetTokenGenerator().make_token(self.user)
                self.valid_url = reverse('password-reset-confirm', args=[self.valid_uid, self.valid_token])

        # 4th request — should now hit throttle limit
        response = self.client.post(self.valid_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_reused_token_returns_error(self):
        response1 = self.client.post(self.valid_url, self.valid_data)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        response2 = self.client.post(self.valid_url, self.valid_data)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response2.data)
        self.assertIn('reset link', str(response2.data['token'][0]).lower())
