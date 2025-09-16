from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import UserFile

User = get_user_model()


class UserAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123",
        )

        # API URLs
        self.signup_url = reverse("api-signup")
        self.login_url = reverse("api-login")
        self.logout_url = reverse("api-logout")
        self.profile_url = reverse("api-profile")
        self.password_reset_url = reverse("api-password-reset")
        self.userfile_url = reverse("api-user-files")

        # UID & token for password reset
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        self.set_new_password_url = reverse(
            "api-set-new-password", args=[uidb64, token]
        )

    def test_signup(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123", 
            "confirm_password": "newpassword123",
            "first_name": "New",
            "middle_name": "User",
            "last_name": "Example",
        }
        response = self.client.post(self.signup_url, data, format="json")
        if response.status_code != status.HTTP_201_CREATED:
            print("Signup failed:", response.data)  # Debug info
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login(self):
        data = {"username": "testuser", "password": "testpassword123"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("username", response.data)
        self.assertEqual(response.data["username"], "testuser")

    def test_logout(self):
        self.client.login(username="testuser", password="testpassword123")
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_get(self):
        self.client.login(username="testuser", password="testpassword123")
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_update(self):
        self.client.login(username="testuser", password="testpassword123")
        data = {"bio": "Hello, I am a test user", "location": "Kenya"}
        response = self.client.put(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("bio"), "Hello, I am a test user")
        self.assertEqual(response.data.get("location"), "Kenya")

    # ---------------- UserFile Tests ----------------
    def test_userfile_upload_and_list(self):
        self.client.login(username="testuser", password="testpassword123")

        file_data = SimpleUploadedFile(
            "resume.txt", b"My resume content", content_type="text/plain"
        )
        data = {"file_type": "resume", "file": file_data}
        response = self.client.post(self.userfile_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserFile.objects.filter(user=self.user).count(), 1)

        response = self.client.get(self.userfile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["file_type"], "resume")

    def test_userfile_delete(self):
        self.client.login(username="testuser", password="testpassword123")

        file_data = SimpleUploadedFile(
            "cv.txt", b"My CV content", content_type="text/plain"
        )
        user_file = UserFile.objects.create(
            user=self.user, file_type="cv", file=file_data
        )

        delete_url = reverse("api-user-file-detail", args=[user_file.id])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserFile.objects.filter(id=user_file.id).exists())
