# jobsboard/jobs/tests.py
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from companies.models import Company, Industry
from jobs.models import Job, Skill, JobSkill

User = get_user_model()


class JobAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a test jobseeker
        self.seeker = User.objects.create_user(
            username="testseeker",
            email="seeker@example.com",
            password="testpass123",
            role=User.ROLE_SEEKER,
        )

        # Create a test employer
        self.employer = User.objects.create_user(
            username="testemployer",
            email="employer@example.com",
            password="testpass123",
            role=User.ROLE_EMPLOYER,
        )

        # Create an Industry instance
        self.industry = Industry.objects.create(name="Healthcare")

        # Create a Company instance
        self.company = Company.objects.create(
            name="Test Company",
            description="Test company description",
            industry=self.industry,
            owner=self.employer,
        )

        # Create a Job instance
        self.job = Job.objects.create(
            title="Test Job",
            description="Test job description",
            company=self.company,
            employment_type="full_time",
            location="Remote",
            salary_min=50000,
            salary_max=100000,
        )

    def test_list_jobs(self):
        """Anyone (public) can list jobs"""
        response = self.client.get(reverse("job-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_apply_to_job_as_seeker(self):
        """Jobseeker should be able to apply to a job"""
        self.client.force_authenticate(user=self.seeker)
        url = reverse("job-apply", args=[self.job.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("applied", response.data["message"])

    def test_apply_to_job_as_employer_forbidden(self):
        """Employer should NOT be able to apply to a job"""
        self.client.force_authenticate(user=self.employer)
        url = reverse("job-apply", args=[self.job.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class JobSkillAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a test user
        self.user = User.objects.create_user(
            username="skilluser",
            email="skilluser@example.com",
            password="testpass123"
        )

        # Create an Industry instance
        self.industry = Industry.objects.create(name="IT")

        # Create a Company instance
        self.company = Company.objects.create(
            name="Skill Company",
            description="Skill company description",
            industry=self.industry,
            owner=self.user,
        )

        # Create a Job instance
        self.job = Job.objects.create(
            title="Skill Job",
            description="Skill job description",
            company=self.company,
            employment_type="part_time",
            location="On-site",
            salary_min=30000,
            salary_max=60000,
        )

        # Create a Skill instance
        self.skill = Skill.objects.create(name="Python")

        # Create JobSkill linking job and skill
        self.job_skill = JobSkill.objects.create(
            job=self.job,
            skill=self.skill
        )

    def test_list_job_skills(self):
        """Anyone (public) can list job skills"""
        response = self.client.get(reverse("jobskill-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
