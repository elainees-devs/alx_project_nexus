#jobboard/applications/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from companies.models import Company, Industry
from jobs.models import Job
from applications.models import Application, ApplicationFile

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


class ApplicationFileTestCase(TestCase):
    def setUp(self):
        # Create seeker user
        self.seeker = User.objects.create_user(
            username="fileuser",
            email="fileuser@example.com",
            password="testpass123",
            role="SEEKER"
        )

        # Create Industry and Company
        self.industry = Industry.objects.create(name="Finance")
        self.company = Company.objects.create(
            name="Finance Inc",
            description="A finance company",
            industry=self.industry,
            owner=self.seeker 
        )

        # Create Job
        self.job = Job.objects.create(
            title="Data Analyst",
            description="Analyze financial data",
            company=self.company,
            employment_type="part_time",
            location="On-site",
            salary_min=40000,
            salary_max=80000
        )

        # Create Application
        self.application = Application.objects.create(
            job=self.job,
            applicant=self.seeker,
            status="pending"
        )

        # Create Application File
        self.app_file = ApplicationFile.objects.create(
            application=self.application,
            file_type="resume",
            file_path="/fake/path/resume.pdf"
        )

    def test_application_file_created(self):
        self.assertEqual(ApplicationFile.objects.count(), 1)
        self.assertEqual(self.app_file.application, self.application)
        self.assertEqual(self.app_file.file_type, "resume")

    def test_str_representation(self):
        self.assertIn("File for", str(self.app_file))
