from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

class UserAPITestCase(APITestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )

        # URLS
        self.signup_url = reverse('api-signup')
        self.login_url = reverse('api-login')
        self.logout_url = reverse('api-logout')
        self.profile_url = reverse('api-profile')
        self.password_reset_url = reverse('api-password-reset')

        # Generate a UID and token for set new password URL
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        self.set_new_password_url = reverse(
            'api-set-new-password', args=[uidb64, token]
        )

    def test_signup(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "confirm_password": "newpassword123",
            "first_name": "New",
            "middle_name": "User",
            "last_name": "Example"
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login(self):
        data = {"username": "testuser", "password": "testpassword123"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('username', response.data)
        self.assertEqual(response.data['username'], 'testuser')

    def test_logout(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Logged out successfully.")

    def test_profile_get(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('bio', ''), '')  # default empty

    def test_profile_update(self):
        self.client.login(username='testuser', password='testpassword123')
        data = {"bio": "Hello, I am a test user", "location": "Kenya"}
        response = self.client.put(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('bio'), "Hello, I am a test user")
        self.assertEqual(response.data.get('location'), "Kenya")

    def test_password_reset_request(self):
        data = {"email": "testuser@example.com"}
        response = self.client.post(self.password_reset_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Password reset link sent", response.data['detail'])
