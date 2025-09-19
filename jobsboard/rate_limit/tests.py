# jobsboard/rate_limit/tests.py
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from rate_limit.models import RateLimit, RateLimitAction
from rate_limit.services import check_rate_limit, RateLimitExceeded

User = get_user_model()


class RateLimitServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass1234"
        )
        self.action = RateLimitAction.objects.create(name="create_job")

    def test_action_within_limit_passes(self):
        """First request should be allowed (no exception)"""
        try:
            check_rate_limit(self.user, "create_job", limit=3, period_seconds=60)
        except Exception as e:
            self.fail(f"check_rate_limit unexpectedly raised {e}")

    def test_exceeding_limit_fails(self):
        """Exceeding limit should raise RateLimitExceeded"""
        for _ in range(3):
            check_rate_limit(self.user, "create_job", limit=3, period_seconds=60)

        with self.assertRaises(RateLimitExceeded):
            check_rate_limit(self.user, "create_job", limit=3, period_seconds=60)

    def test_limit_resets_after_period(self):
        """Rate limit should reset after period expires"""
        check_rate_limit(self.user, "create_job", limit=1, period_seconds=1)
        rl = RateLimit.objects.get(user=self.user, action=self.action)

        # Manually expire the period
        rl.period_start = timezone.now() - timezone.timedelta(seconds=2)
        rl.save()

        try:
            check_rate_limit(self.user, "create_job", limit=1, period_seconds=1)
        except Exception as e:
            self.fail(f"check_rate_limit unexpectedly raised {e}")


class RateLimitViewSetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="apitest", email="api@example.com", password="pass1234"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_within_limit(self):
        """API allows request within limit"""
        response = self.client.post("/api/rate-limit/create_job/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_exceed_limit(self):
        """API blocks requests exceeding limit"""
        # Exceed by calling multiple times
        for _ in range(5):
            self.client.post("/api/rate-limit/create_job/")

        response = self.client.post("/api/rate-limit/create_job/")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
