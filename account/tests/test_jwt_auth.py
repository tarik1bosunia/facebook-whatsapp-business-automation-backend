from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
import json

User = get_user_model()

class JWTAuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='strongpassword123'
        )
        self.token_url = reverse('token_obtain_pair')
        self.token_refresh_url = reverse('token_refresh')
        self.token_verify_url = reverse('token_verify')

    def test_token_obtain_pair(self):
        response = self.client.post(self.token_url, {
            "email": "test@example.com",
            "password": "strongpassword123"
        }, format='json')

        data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', data)
        self.assertIn('refresh', data)

    def test_token_refresh(self):
        # First obtain token
        response = self.client.post(self.token_url, {
            "email": "test@example.com",
            "password": "strongpassword123"
        }, format='json')

        refresh = json.loads(response.content)['refresh']

        # Now refresh it
        response = self.client.post(self.token_refresh_url, {
            "refresh": refresh
        }, format='json')

        data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', data)

    def test_token_verify(self):
        # First obtain access token
        response = self.client.post(self.token_url, {
            "email": "test@example.com",
            "password": "strongpassword123"
        }, format='json')

        access = json.loads(response.content)['access']

        # Now verify with access token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.post(self.token_verify_url)

        data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', data)
        self.assertIn('access', data['token'])
        self.assertIn('refresh', data['token'])
        self.assertEqual(data['message'], 'User is verified')
