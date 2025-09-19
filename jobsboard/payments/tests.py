#jobsboard/payments/tests.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch
from payments.models import Payment

User = get_user_model()


class PaymentAPITestCase(APITestCase):
    """
    Tests for payment initiation, verification, and verified list
    """

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Router-generated URLs (basename='payment')
        self.initiate_url = reverse("payment-initiate")
        self.verify_url = reverse("payment-verify")
        self.list_verified_url = reverse("payment-verified")

    @patch("requests.post")
    def test_initiate_payment(self, mock_post):
        """Test initiating a Chapaa payment"""
        # Mock Chapaa API response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "status": "success",
            "data": {
                "tx_ref": "chapaa123",
                "checkout_url": "https://chapa.checkout/123"
            }
        }

        payload = {
            "amount": 50.00,
            "currency": "USD",
            "description": "Premium job posting",
            "payment_type": "job_posting",
            "metadata": {"job_id": 101}
        }

        response = self.client.post(self.initiate_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("payment", response.data)
        self.assertEqual(response.data["payment"]["provider"], "chapaa")
        self.assertEqual(response.data["payment"]["payment_type"], "job_posting")

    @patch("requests.get")
    def test_verify_payment(self, mock_get):
        """Test verifying a Chapaa payment"""
        # Create a pending payment first
        payment = Payment.objects.create(
            user=self.user,
            provider="chapaa",
            payment_type="premium_subscription",
            amount=20.0,
            transaction_id="chapaa456",
            status="pending",
            metadata={"plan": "monthly_premium"}
        )

        # Mock Chapaa verify response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "status": "success",
            "data": {"tx_ref": "chapaa456"}
        }

        payload = {"transaction_id": "chapaa456"}
        response = self.client.post(self.verify_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")

        payment.refresh_from_db()
        self.assertEqual(payment.status, "completed")

    def test_list_verified_payments(self):
        """Test listing all completed payments for user"""
        Payment.objects.create(
            user=self.user,
            provider="chapaa",
            payment_type="job_posting",
            amount=50,
            status="completed",
            transaction_id="tx1"
        )
        Payment.objects.create(
            user=self.user,
            provider="chapaa",
            payment_type="premium_subscription",
            amount=20,
            status="pending",
            transaction_id="tx2"
        )

        response = self.client.get(self.list_verified_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "completed")
        self.assertEqual(response.data[0]["provider"], "chapaa")


class PaymentPermissionTests(APITestCase):
    """
    Tests for PaymentPermission rules:
    - Normal users cannot update/delete payments
    - Admins can manage all payments
    - Anonymous users cannot access
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="normaluser",
            email="normal@example.com",
            password="testpass123"
        )
        self.admin = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="adminpass123"
        )
        self.payment = Payment.objects.create(
            user=self.user,
            provider="chapaa",
            payment_type="job_posting",
            amount=100,
            status="completed",
            transaction_id="tx100"
        )
        self.client = APIClient()

        # Router-generated names: basename='payment'
        self.list_url = reverse("payment-list")
        self.detail_url = reverse("payment-detail", args=[self.payment.id])

    def test_normal_user_cannot_delete_payment(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_normal_user_cannot_update_payment(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url, {"status": "failed"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_payment(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_view_all_payments(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_unauthenticated_cannot_access(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
