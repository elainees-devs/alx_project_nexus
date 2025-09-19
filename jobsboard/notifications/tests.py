# jobsboard/notifications/tests.py
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from notifications.models import Notification
from companies.models import Company

User = get_user_model()


class NotificationAPITestCase(APITestCase):
    def setUp(self):
        # Create users for each role
        self.seeker = User.objects.create_user(
            username="seeker",
            email="seeker@example.com",
            password="testpass123",
            role=User.ROLE_SEEKER,
        )
        self.employer = User.objects.create_user(
            username="employer",
            email="employer@example.com",
            password="testpass123",
            role=User.ROLE_EMPLOYER,
        )
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="testpass123",
        )

        # Company setup: link seeker → employer
        self.company = Company.objects.create(
            name="Test Company",
            description="A sample company for testing",
            industry=None,  # adjust if Industry is required
            location="Test Location",
            owner=self.employer,
            logo="company_logos/test.png",
        )
        self.seeker.company = self.company
        self.seeker.save()

        # URLs
        self.list_url = reverse("notification-list")

        # Sample notification (belongs to seeker)
        self.notification = Notification.objects.create(
            user=self.seeker,
            title="Test Notification",
            message="This is a test notification",
        )

    def authenticate(self, user):
        """Helper to authenticate client as given user."""
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    # -----------------------------
    # Seeker Tests
    # -----------------------------
    def test_seeker_can_list_and_retrieve(self):
        self.authenticate(self.seeker)
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

        url = reverse("notification-detail", args=[self.notification.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_seeker_cannot_create_update_or_delete(self):
        self.authenticate(self.seeker)

        # Create
        payload = {"title": "New", "message": "Nope"}
        res = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Update
        url = reverse("notification-detail", args=[self.notification.id])
        res = self.client.put(url, {"title": "Changed"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Delete
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # -----------------------------
    # Employer Tests
    # -----------------------------
    def test_employer_can_create_update_and_delete(self):
        self.authenticate(self.employer)

        # Create
        payload = {"title": "Employer Notice", "message": "Hello"}
        res = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Update
        url = reverse("notification-detail", args=[self.notification.id])
        res = self.client.patch(url, {"title": "Employer Updated"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Delete
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_employer_cannot_access_other_company_notifications(self):
        # Create another seeker in a different company
        other_employer = User.objects.create_user(
            username="other_employer",
            email="other_employer@example.com",
            password="testpass123",
            role=User.ROLE_EMPLOYER,
        )
        other_company = Company.objects.create(
            name="Other Company",
            description="Another test company",
            industry=None,
            location="Other Location",
            owner=other_employer,
            logo="company_logos/other.png",
        )
        outsider = User.objects.create_user(
            username="outsider",
            email="outsider@example.com",
            password="testpass123",
            role=User.ROLE_SEEKER,
            company=other_company,
        )
        outsider_notification = Notification.objects.create(
            user=outsider,
            title="Outsider Notification",
            message="Not visible to first employer",
        )

        self.authenticate(self.employer)
        url = reverse("notification-detail", args=[outsider_notification.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    # -----------------------------
    # Admin Tests
    # -----------------------------
    def test_admin_can_do_everything(self):
        self.authenticate(self.admin)

        # Create
        payload = {"title": "Admin Notice", "message": "System-wide"}
        res = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Update
        url = reverse("notification-detail", args=[self.notification.id])
        res = self.client.put(
            url, {"title": "Admin Updated", "message": "Ok"}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Delete
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    # -----------------------------
    # Mark as Read
    # -----------------------------
    def test_mark_as_read(self):
        self.authenticate(self.seeker)  # allowed (on own notification)
        url = reverse("notification-mark-as-read", args=[self.notification.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
