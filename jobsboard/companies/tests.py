#jobsboard/companies/test.py
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from companies.models import Industry, Company

User = get_user_model()


class IndustryAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password"
        )
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password"
        )
        self.admin.is_staff = True
        self.admin.save()

        self.client = APIClient()
        self.industry_url = "/api/industries/"
        self.industry = Industry.objects.create(name="Tech")

    def test_get_industries(self):
        response = self.client.get(self.industry_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_industry(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "Finance"}
        response = self.client.post(self.industry_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_industry(self):
        self.client.force_authenticate(user=self.user)
        url = f"{self.industry_url}{self.industry.pk}/"
        data = {"name": "Updated Tech"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_industry(self):
        self.client.force_authenticate(user=self.admin) 
        url = f"{self.industry_url}{self.industry.pk}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CompanyAPITestCase(APITestCase):
    def setUp(self):
        self.industry = Industry.objects.create(name="Tech")
        self.company_url = "/api/companies/"

        # Create users with different roles
        self.seeker = User.objects.create_user(
            username="seeker",
            email="seeker@example.com",
            password="password",
            role="seeker"
        )
        self.employer = User.objects.create_user(
            username="employer",
            email="employer@example.com",
            password="password",
            role="employer"
        )
        self.admin = User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="password"
        )
        self.admin.is_staff = True
        self.admin.save()


        # Create a company owned by employer
        self.company = Company.objects.create(
            name="Example Co",
            description="Test company",
            industry=self.industry,
            owner=self.employer
        )

    def test_employer_can_create_company(self):
        self.client.force_authenticate(user=self.employer)
        payload = {
            "name": "Employer Co",
            "description": "Created by employer",
            "industry": self.industry.id
        }
        response = self.client.post(self.company_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_seeker_cannot_create_company(self):
        self.client.force_authenticate(user=self.seeker)
        payload = {
            "name": "Invalid Co",
            "description": "Seeker should not create",
            "industry": self.industry.id
        }
        response = self.client.post(self.company_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_company(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            "name": "Admin Co",
            "description": "Created by admin",
            "industry": self.industry.id
        }
        response = self.client.post(self.company_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_employer_can_update_company(self):
        self.client.force_authenticate(user=self.employer)
        url = f"{self.company_url}{self.company.pk}/"
        data = {
            "name": "Updated Employer Co",
            "description": "Updated description",
            "industry": self.industry.id
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_seeker_cannot_update_company(self):
        self.client.force_authenticate(user=self.seeker)
        url = f"{self.company_url}{self.company.pk}/"
        data = {
            "name": "Seeker Update",
            "description": "Should be forbidden",
            "industry": self.industry.id
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_company(self):
        self.client.force_authenticate(user=self.admin)
        url = f"{self.company_url}{self.company.pk}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_employer_cannot_delete_company(self):
        self.client.force_authenticate(user=self.employer)
        url = f"{self.company_url}{self.company.pk}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_companies_public(self):
        response = self.client.get(self.company_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
