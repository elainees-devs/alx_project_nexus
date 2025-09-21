# jobsboard/analytics/tests.py
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from django.utils import timezone
from jobs.models import Job
from analytics.models import JobViewAggregate, JobApplicationAggregate
from django.contrib.auth import get_user_model
from companies.models import Company, Industry

User = get_user_model()


class AnalyticsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Users
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@test.com", password="admin123"
        )
        self.employer = User.objects.create_user(
            username="employer", email="employer@test.com", password="employer123", role=User.ROLE_EMPLOYER
        )
        self.seeker = User.objects.create_user(
            username="seeker", email="seeker@test.com", password="seeker123", role=User.ROLE_SEEKER
        )

        # Industry and Company
        self.industry = Industry.objects.create(name="Tech")
        self.company = Company.objects.create(
            name="Tech Co",
            description="Test",
            industry=self.industry,
            owner=self.employer
        )

        # Job
        self.job = Job.objects.create(
            title="Test Job",
            description="Job description",
            company=self.company,
            employment_type="full_time",
            location="Remote",
            salary_min=50000,
            salary_max=100000,
            status="open",
            created_by=self.employer
        )

        # Aggregates
        self.view_aggregate = JobViewAggregate.objects.create(
            job=self.job,
            date=timezone.now().date(),
            view_count=15
        )
        self.application_aggregate = JobApplicationAggregate.objects.create(
            job=self.job,
            date=timezone.now().date(),
            application_count=5
        )

    # -----------------------------
    # Job Views Tests
    # -----------------------------
    def test_admin_can_view_job_views(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("job-views-list-views")  # matches router basename 'job-views' + action 'list_views'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['view_count'], 15)

    def test_employer_can_view_their_job_views(self):
        self.client.force_authenticate(user=self.employer)
        url = reverse("job-views-list-views")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['job_title'], "Test Job")

    def test_employer_cannot_view_others_job_views(self):
        other_employer = User.objects.create_user(
            username="other", email="other@test.com", password="other123", role=User.ROLE_EMPLOYER
        )
        self.client.force_authenticate(user=other_employer)
        url = reverse("job-views-list-views")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # -----------------------------
    # Job Applications Tests
    # -----------------------------
    def test_admin_can_view_job_applications(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("job-applications-list-applications")  # matches router basename 'job-applications' + action 'list_applications'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['application_count'], 5)

    def test_employer_can_view_their_job_applications(self):
        self.client.force_authenticate(user=self.employer)
        url = reverse("job-applications-list-applications")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['job_title'], "Test Job")

    def test_employer_cannot_view_others_job_applications(self):
        other_employer = User.objects.create_user(
            username="other2", email="other2@test.com", password="other123", role=User.ROLE_EMPLOYER
        )
        self.client.force_authenticate(user=other_employer)
        url = reverse("job-applications-list-applications")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
