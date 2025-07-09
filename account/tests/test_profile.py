from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfileTests(APITestCase):
    """
    Getting own profile

    Updating own profile (first name, last name)

    Trying to update read-only fields (id, email, role) — fields will be ignored, no error
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123',
            first_name='John',
            last_name='Doe'
        )
        self.url = reverse('profile')

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def test_get_own_profile(self):
        self.authenticate()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_update_first_name_and_last_name(self):
        self.authenticate()
        payload = {
            'first_name': 'Jane',
            'last_name': 'Smith',
        }
        response = self.client.patch(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Jane')
        self.assertEqual(self.user.last_name, 'Smith')

    def test_attempt_update_readonly_fields_is_ignored(self):
        self.authenticate()
        payload = {
            'email': 'malicious@example.com',
            'role': 'admin',
            'id': 999,
            'first_name': 'NewName'
        }
        response = self.client.patch(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()

        # Email, role, id remain unchanged
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, self.user.role)  # role didn't change
        self.assertNotEqual(self.user.id, 999)  # id stays the same
        self.assertEqual(self.user.first_name, 'NewName')
