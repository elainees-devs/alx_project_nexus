# jobsboard/applications/tests.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from applications.models import Application, ApplicationFile
from jobs.models import Job
from companies.models import Company, Industry

User = get_user_model()

class ApplicationTestCase(TestCase):
    def setUp(self):
        # Create seeker user
        self.seeker = User.objects.create_user(
            username="seeker",
            email="seeker@example.com",
            password="testpass123",
            role="SEEKER"
        )

        # Create recruiter user
        self.recruiter = User.objects.create_user(
            username="recruiter",
            email="recruiter@example.com",
            password="testpass123",
            role="RECRUITER"
        )

        # Create Industry
        self.industry = Industry.objects.create(name="Software")

        # Create Company with recruiter as owner
        self.company = Company.objects.create(
            name="Tech Corp",
            description="A software company",
            industry=self.industry,
            owner=self.recruiter
        )

        # Create Job
        self.job = Job.objects.create(
            title="Backend Developer",
            description="Build APIs",
            company=self.company,
            employment_type="full_time",
            location="Remote",
            salary_min=70000,
            salary_max=120000
        )

        # Create Application
        self.application = Application.objects.create(
            job=self.job,
            applicant=self.seeker,
            cover_letter="I am excited to apply",
            status="pending"
        )

    def test_application_created(self):
        self.assertEqual(Application.objects.count(), 1)
        self.assertEqual(self.application.applicant.username, "seeker")
        self.assertEqual(self.application.job.title, "Backend Developer")

    def test_application_unique_constraint(self):
        """Ensure same user cannot apply to same job twice"""
        with self.assertRaises(Exception):  # IntegrityError
            Application.objects.create(
                job=self.job,
                applicant=self.seeker,
                status="pending"
            )


class ApplicationFileTests(TestCase):
    """Tests for ApplicationFile API."""

    def setUp(self):
        self.client = APIClient()

        # ✅ Add email for seeker
        self.seeker = User.objects.create_user(
            username="seeker",
            email="seeker@test.com",
            password="pass123",
            role="SEEKER"
        )

        # ✅ Add email for recruiter
        self.recruiter = User.objects.create_user(
            username="recruiter",
            email="recruiter@test.com",
            password="pass123",
            role="RECRUITER"
        )

        # ✅ Industry required for Company
        self.industry = Industry.objects.create(name="Tech")
        self.company = Company.objects.create(
            name="Test Company",
            owner=self.recruiter,
            industry=self.industry
        )

        # Job
        self.job = Job.objects.create(title="Backend Developer", company=self.company)

        # Application
        self.application = Application.objects.create(
            job=self.job,
            applicant=self.seeker,
            status="pending"
        )

        self.file_url = reverse("applicationfile-list")

    def test_seeker_can_upload_file(self):
        """Seeker should upload a resume to their application."""
        self.client.force_authenticate(user=self.seeker)
        with open("test_resume.pdf", "wb") as f:
            f.write(b"fake content")

        with open("test_resume.pdf", "rb") as f:
            response = self.client.post(
                self.file_url,
                {
                    "application": self.application.id,
                    "file_type": "resume",
                    "file": f,
                },
                format="multipart"
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ApplicationFile.objects.count(), 1)

    def test_recruiter_cannot_upload_file(self):
        """Recruiter should not upload files to applications."""
        self.client.force_authenticate(user=self.recruiter)
        response = self.client.post(
            self.file_url,
            {"application": self.application.id, "file_type": "resume"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)