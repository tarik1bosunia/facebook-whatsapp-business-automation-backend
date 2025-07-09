from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
import json


User = get_user_model()

class UserLoginViewTest(APITestCase):

    def setUp(self):
        self.login_url = reverse('login')
        self.user_password = "StrongPassword123"
        self.user = User.objects.create_user(
            email="user@example.com",
            password=self.user_password,
            first_name="Test",
            last_name="User"
        )

    @patch('account.utils.Util.get_tokens_for_user')
    def test_login_success(self, mock_get_tokens):
        mock_get_tokens.return_value = {
            "access": "mocked-access-token",
            "refresh": "mocked-refresh-token"
        }

        payload = {
            "email": "user@example.com",
            "password": self.user_password
        }

        response = self.client.post(self.login_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Login Success")
        self.assertIn("token", response.data)
        self.assertIn("access", response.data["token"])
        self.assertIn("refresh", response.data["token"])
        mock_get_tokens.assert_called_once_with(self.user)

    def test_login_invalid_password(self):
        payload = {
            "email": "user@example.com",
            "password": "WrongPassword"
        }

        response = self.client.post(self.login_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("errors", response.data)
        self.assertIn("non_field_errors", response.data["errors"])
        self.assertEqual(
            response.data["errors"]["non_field_errors"][0],
            "Email or Password is not Valid"
        )



    def test_login_missing_fields(self):
        payload = {}

        response = self.client.post(self.login_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Parse actual rendered JSON content
        data = json.loads(response.content)

        self.assertIn("errors", data)
        self.assertIn("email", data["errors"])
        self.assertIn("password", data["errors"])
        self.assertIn("This field is required.", data["errors"]["email"])
        self.assertIn("This field is required.", data["errors"]["password"])



    def test_login_blank_fields(self):
        payload = {
            "email": "",
            "password": ""
        }

        response = self.client.post(self.login_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = json.loads(response.content)

        self.assertIn("errors", data)
        self.assertIn("email", data["errors"])
        self.assertIn("password", data["errors"])
        self.assertIn("This field may not be blank.", data["errors"]["email"])
        self.assertIn("This field may not be blank.", data["errors"]["password"])  