from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import UserFile, Profile

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

    # ---------------- SignUp/Login/Logout/Profile ----------------
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
    def test_userfile_upload_valid_resume(self):
        self.client.login(username="testuser", password="testpassword123")

        file_data = SimpleUploadedFile(
            "resume.pdf", b"%PDF-1.4 fake pdf content", content_type="application/pdf"
        )
        data = {"file_type": "resume", "file": file_data}
        response = self.client.post(self.userfile_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserFile.objects.filter(user=self.user).count(), 1)

    def test_userfile_upload_invalid_resume_type(self):
        self.client.login(username="testuser", password="testpassword123")

        file_data = SimpleUploadedFile(
            "resume.txt", b"invalid file", content_type="text/plain"
        )
        data = {"file_type": "resume", "file": file_data}
        response = self.client.post(self.userfile_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_userfile_upload_large_file(self):
        self.client.login(username="testuser", password="testpassword123")

        large_content = b"x" * 6 * 1024 * 1024  # 6MB
        file_data = SimpleUploadedFile(
            "resume.pdf", large_content, content_type="application/pdf"
        )
        data = {"file_type": "resume", "file": file_data}
        response = self.client.post(self.userfile_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_userfile_delete(self):
        self.client.login(username="testuser", password="testpassword123")

        file_data = SimpleUploadedFile(
            "cv.pdf", b"%PDF-1.4 fake cv content", content_type="application/pdf"
        )
        user_file = UserFile.objects.create(
            user=self.user, file_type="cv", file=file_data
        )

        delete_url = reverse("api-user-file-detail", args=[user_file.id])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserFile.objects.filter(id=user_file.id).exists())

    # ---------------- Profile Image Test ----------------
    def test_profile_image_upload_and_resize(self):
        self.client.login(username="testuser", password="testpassword123")
        image_content = b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x0A\x00\x01\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B"
        profile_image = SimpleUploadedFile(
            "profile.jpg", image_content, content_type="image/jpeg"
        )
        data = {"profile_image": profile_image}
        response = self.client.put(self.profile_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.profile.profile_image.name.endswith(".jpg"))
