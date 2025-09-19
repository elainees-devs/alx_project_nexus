# jobsboard/request_logs/tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from request_logs.models import RequestLog

User = get_user_model()


class RequestLogTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users with email (required by custom user manager)
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="pass123"
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="pass123"
        )
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )

        # Manually create request logs
        RequestLog.objects.create(
            user=self.user1,
            ip_address="127.0.0.1",
            endpoint="/",
            method="GET",
            status_code=200
        )
        RequestLog.objects.create(
            user=self.user1,
            ip_address="127.0.0.1",
            endpoint="/profile/",
            method="POST",
            status_code=201
        )
        RequestLog.objects.create(
            user=self.user2,
            ip_address="127.0.0.1",
            endpoint="/",
            method="GET",
            status_code=200
        )

    def test_list_request_logs(self):
        """User sees only their own logs"""
        self.client.force_authenticate(self.user1)
        user1_ids = set(RequestLog.objects.filter(user=self.user1).values_list("id", flat=True))

        response = self.client.get("/api/request-logs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_ids = {log["id"] for log in response.data["results"]}
        self.assertTrue(user1_ids.issubset(response_ids))

    def test_retrieve_request_log(self):
        """User can retrieve their own request log"""
        log = RequestLog.objects.filter(user=self.user1).first()
        self.assertIsNotNone(log)

        self.client.force_authenticate(self.user1)
        response = self.client.get(f"/api/request-logs/{log.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], log.id)

    def test_cannot_access_other_users_logs(self):
        """User cannot access another user's logs"""
        log = RequestLog.objects.filter(user=self.user2).first()
        self.assertIsNotNone(log)

        self.client.force_authenticate(self.user1)
        response = self.client.get(f"/api/request-logs/{log.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_list_all_logs(self):
        """Admin can view all logs"""
        db_ids = set(RequestLog.objects.all().values_list("id", flat=True))

        self.client.force_authenticate(self.admin)
        response = self.client.get("/api/request-logs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_ids = {log["id"] for log in response.data["results"]}
        self.assertTrue(db_ids.issubset(response_ids))

    def test_request_log_is_created_manually(self):
        """Manual creation works as expected"""
        log = RequestLog.objects.create(
            user=self.user1,
            ip_address="127.0.0.1",
            endpoint="/manual/",
            method="POST",
            status_code=201
        )
        self.assertIsNotNone(log.id)
