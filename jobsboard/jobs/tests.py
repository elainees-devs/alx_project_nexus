from django.test import TestCase
from django.contrib.auth import get_user_model
from companies.models import Company, Industry
from jobs.models import Job, Skill, JobSkill

User = get_user_model()

class JobAPITestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass123"
        )

        # Create an Industry instance
        self.industry = Industry.objects.create(name="Healthcare")

        # Create a Company instance with owner and industry
        self.company = Company.objects.create(
            name="Test Company",
            description="Test company description",
            industry=self.industry,
            owner=self.user
        )

        # Create a Job instance
        self.job = Job.objects.create(
            title="Test Job",
            description="Test job description",
            company=self.company,
            employment_type="full_time",
            location="Remote",
            salary_min=50000,
            salary_max=100000
        )

class JobSkillAPITestCase(TestCase):
    def setUp(self):
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
            owner=self.user
        )

        # Create a Job instance
        self.job = Job.objects.create(
            title="Skill Job",
            description="Skill job description",
            company=self.company,
            employment_type="part_time",
            location="On-site",
            salary_min=30000,
            salary_max=60000
        )

        # Create a Skill instance
        self.skill = Skill.objects.create(name="Python")

        # Create JobSkill linking job and skill
        self.job_skill = JobSkill.objects.create(
            job=self.job,
            skill=self.skill
        )
