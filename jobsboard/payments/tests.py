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
    self.list_url = reverse("payment-verified")



    @patch("requests.post")
    def test_initiate_payment(self, mock_post):
        """
        Test initiating a Chapaa payment
        """
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
        """
        Test verifying a Chapaa payment
        """
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

        payload = {
            "transaction_id": "chapaa456"
        }

        response = self.client.post(self.verify_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")

        # Refresh from DB
        payment.refresh_from_db()
        self.assertEqual(payment.status, "completed")

    def test_list_verified_payments(self):
        """
        Test listing all completed payments for user
        """
        # Create completed and pending payments
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

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "completed")
        self.assertEqual(response.data[0]["provider"], "chapaa")
