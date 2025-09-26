import uuid
from unittest.mock import patch
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import User
from payments.models import Payment


class PaymentAPITest(APITestCase):

    def setUp(self):
        self.seeker = User.objects.create_user(
            username="seek1", email="seek1@example.com",
            password="pass1234", role=User.ROLE_SEEKER
        )
        self.employer = User.objects.create_user(
            username="emp1", email="emp1@example.com",
            password="pass1234", role=User.ROLE_EMPLOYER
        )
        self.admin = User.objects.create_user(
            username="admin1", email="admin1@example.com",
            password="pass1234", role=User.ROLE_ADMIN
        )

        self.initiate_url = reverse("payment-initiate-payment")
        self.list_url = reverse("payment-list")

        self.payment_payload = {
            "amount": "500.00",
            "currency": "ETB",
            "email": "seek1@example.com",
            "first_name": "Seek",
            "last_name": "User",
            "phone_number": "0912345678",
            "tx_ref": f"test-{uuid.uuid4()}",
            "callback_url": "https://webhook.site/test-callback",
            "return_url": "https://example.com/return",
            "customization": {
                "title": "Payment for Job Posting",
                "description": "Testing payment"
            }
        }

    @patch("payments.views.ChapaAPI.initialize_payment")
    def test_user_can_initiate_payment(self, mock_initialize_payment):
        mock_initialize_payment.return_value = {
            "status": "success",
            "data": {"checkout_url": "https://fake.chapa/checkout/12345"}
        }

        self.client.login(username="seek1", password="pass1234")
        response = self.client.post(self.initiate_url, self.payment_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("checkout_url", response.data)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(Payment.objects.first().user, self.seeker)

    def test_anonymous_cannot_initiate_payment(self):
        response = self.client.post(self.initiate_url, self.payment_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("payments.views.ChapaAPI.initialize_payment")
    def test_user_only_sees_their_own_payments(self, mock_initialize_payment):
        mock_initialize_payment.return_value = {
            "status": "success",
            "data": {"checkout_url": "https://fake.chapa/checkout/12345"}
        }

        # Seeker initiates
        self.client.login(username="seek1", password="pass1234")
        self.client.post(self.initiate_url, self.payment_payload, format="json")

        # Employer initiates
        self.client.login(username="emp1", password="pass1234")
        payload_emp = self.payment_payload.copy()
        payload_emp["tx_ref"] = f"test-{uuid.uuid4()}"
        payload_emp["email"] = "emp1@example.com"
        self.client.post(self.initiate_url, payload_emp, format="json")

        # Seeker lists → should only see their own
        self.client.login(username="seek1", password="pass1234")
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        for p in results:
            self.assertEqual(p["user"], self.seeker.id)

    @patch("payments.views.ChapaAPI.verify_payment")
    def test_verify_payment(self, mock_verify_payment):
        # Create a payment
        payment = Payment.objects.create(
            user=self.seeker,
            amount=100,
            currency="ETB",
            email="seek1@example.com",
            first_name="Seek",
            last_name="User",
            phone_number="0912345678",
            tx_ref=f"tx-{uuid.uuid4()}",
            callback_url="https://webhook.site/test",
            return_url="https://example.com/return",
            customization={"title": "Test", "description": "Testing"}
        )

        mock_verify_payment.return_value = {
            "status": "success",
            "data": {"status": "success"}
        }

        url = reverse("payment-verify-payment", args=[payment.id])
        self.client.login(username="admin1", password="pass1234")
        response = self.client.post(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("verification", response.data)
        self.assertIn("payment", response.data)
