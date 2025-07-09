from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationTest(APITestCase):
    def setUp(self):
        self.registration_url = reverse('registration')
        self.valid_payload = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "StrongPassword123"
        }
        self.invalid_payload = {
            "email": "invalidemail",
            "first_name": "",
            "last_name": "User",
            "password": "123"  # too short
        }

    def test_user_registration_success(self):
        response = self.client.post(self.registration_url, self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], self.valid_payload["email"])
        self.assertTrue(User.objects.filter(email=self.valid_payload["email"]).exists())

    def test_user_registration_validation_error(self):
        response = self.client.post(self.registration_url, self.invalid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertIn("email", response.data)

    def test_duplicate_email_registration(self):
        # Create a user first
        User.objects.create_user(**self.valid_payload)

        response = self.client.post(self.registration_url, self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

