# jobsboard/request_logs/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import RequestLog

User = get_user_model()

class RequestLogTests(TestCase):
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create_user(username="user1", email="user1@example.com", password="pass123")
        self.user2 = User.objects.create_user(username="user2", email="user2@example.com", password="pass123")

        self.client = APIClient()
        self.client.force_authenticate(self.user1)

        self.log_data = {
            "ip_address": "127.0.0.1",
            "endpoint": "/api/test/",
            "method": "GET",
            "status_code": 200
        }

    def test_create_request_log(self):
        """Authenticated user can create a request log"""
        response = self.client.post("/api/request-logs/log/", self.log_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RequestLog.objects.count(), 1)
        self.assertEqual(RequestLog.objects.first().user, self.user1)

    def test_list_request_logs(self):
        """User can list their own request logs"""
        RequestLog.objects.create(user=self.user1, **self.log_data)
        RequestLog.objects.create(user=self.user2, **self.log_data)

        response = self.client.get("/api/request-logs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["ip_address"], "127.0.0.1")

    def test_retrieve_request_log(self):
        """User can retrieve their own request log"""
        log = RequestLog.objects.create(user=self.user1, **self.log_data)
        response = self.client.get(f"/api/request-logs/{log.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["endpoint"], "/api/test/")

    def test_cannot_access_other_users_logs(self):
        """User cannot access other users' logs"""
        log = RequestLog.objects.create(user=self.user2, **self.log_data)
        response = self.client.get(f"/api/request-logs/{log.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
