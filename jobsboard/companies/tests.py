# jobsboard/companies/tests.py
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
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.industry_url = "/api/companies/industries/"
        self.industry = Industry.objects.create(name="Tech")

    def test_get_industries(self):
        response = self.client.get(self.industry_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_industry(self):
        data = {"name": "Finance"}
        response = self.client.post(self.industry_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_industry(self):
        url = f"{self.industry_url}{self.industry.pk}/"
        data = {"name": "Updated Tech"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_industry(self):
        url = f"{self.industry_url}{self.industry.pk}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CompanyAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password"
        )
        self.client.force_authenticate(user=self.user)  # authenticate the user

        self.industry = Industry.objects.create(name="Tech")

        # Create a company
        self.company = Company.objects.create(
            name="Example Co",
            description="Test company",
            industry=self.industry,
            owner=self.user
        )

        # Update company_url to match the new URLs
        self.company_url = "/api/companies/"

    def test_create_company(self):
        payload = {
            "name": "New Company",
            "description": "Created in test",
            "industry": self.industry.id
        }
        response = self.client.post(self.company_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_companies(self):
        response = self.client.get(self.company_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_company(self):
        url = f"{self.company_url}{self.company.pk}/"
        data = {
            "name": "Updated Co",
            "industry": self.industry.id,
            "description": "Updated description"
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_company(self):
        url = f"{self.company_url}{self.company.pk}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
