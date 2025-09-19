# jobsboard/notifications/tests.py
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()


class NotificationAPITestCase(APITestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Router-generated URLs (basename='notification')
        self.list_url = reverse("notification-list")
        # detail/retrieve/update/destroy URLs will be built with args

        # Create a sample notification
        self.notification = Notification.objects.create(
            user=self.user,
            title="Test Notification",
            message="This is a test notification"
        )

    def test_list_notifications(self):
        """
        Test listing all notifications for the authenticated user
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Notification")

    def test_retrieve_notification(self):
        """
        Test retrieving a single notification
        """
        url = reverse("notification-detail", args=[self.notification.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.notification.id)
        self.assertEqual(response.data["title"], "Test Notification")

    def test_create_notification(self):
        """
        Test creating a new notification
        """
        payload = {
            "title": "New Notification",
            "message": "Hello world"
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), 2)
        created = Notification.objects.get(id=response.data["id"])
        self.assertEqual(created.user, self.user)
        self.assertEqual(created.title, "New Notification")

    def test_update_notification(self):
        """
        Test updating a notification
        """
        url = reverse("notification-detail", args=[self.notification.id])
        payload = {"title": "Updated Title", "message": "Updated message"}
        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.title, "Updated Title")

    def test_partial_update_notification(self):
        """
        Test partially updating a notification
        """
        url = reverse("notification-detail", args=[self.notification.id])
        payload = {"title": "Partially Updated"}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.title, "Partially Updated")

    def test_delete_notification(self):
        """
        Test deleting a notification
        """
        url = reverse("notification-detail", args=[self.notification.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Notification.objects.count(), 0)

    def test_mark_as_read(self):
        """
        Test marking a notification as read
        """
        url = reverse("notification-mark-as-read", args=[self.notification.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
        self.assertEqual(response.data["status"], "read")
