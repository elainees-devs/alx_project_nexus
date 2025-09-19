# jobsboard/payments/views.py
import time
import json
import logging
import requests
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings

from .models import Payment
from .permissions import PaymentPermission
from .serializers import PaymentSerializer, PaymentInputSerializer, PaymentVerifySerializer

logger = logging.getLogger(__name__)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for Chapaa payments:
    - list (all payments for user)
    - retrieve (single payment)
    - initiate payment (custom)
    - verify payment (custom)
    - verified payments (custom)
    """
    serializer_class = PaymentSerializer
    permission_classes = [PaymentPermission]
    queryset = Payment.objects.all()

    # Users only see their own payments
    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Payment.objects.all()
        return Payment.objects.filter(user=self.request.user)

    # -------------------------
    # List & Retrieve & CRUD
    # -------------------------
    @swagger_auto_schema(security=[{"Bearer": []}])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(security=[{"Bearer": []}])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(security=[{"Bearer": []}])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(security=[{"Bearer": []}])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(security=[{"Bearer": []}])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(security=[{"Bearer": []}])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    # -------------------------
    # Initiate Payment
    # -------------------------
    @swagger_auto_schema(
        methods=['post'],
        request_body=PaymentInputSerializer,
        responses={201: PaymentSerializer},
        operation_description="Initiate Chapaa payment for job posting or premium subscription",
        security=[{"Bearer": []}]
    )
    @action(detail=False, methods=['post'], url_path='initiate')
    def initiate(self, request):
        serializer = PaymentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["amount"]
        currency = serializer.validated_data.get("currency", "USD")
        description = serializer.validated_data.get("description", "")
        metadata = serializer.validated_data.get("metadata", {})
        payment_type = serializer.validated_data["payment_type"]

        # Prevent duplicate payment
        if Payment.objects.filter(user=request.user, metadata=metadata).exists():
            return Response({"error": "Payment already exists"}, status=status.HTTP_400_BAD_REQUEST)

        payment_ref = f"{payment_type}_{int(time.time())}"
        payload = {
            "amount": str(amount),
            "currency": currency,
            "email": request.user.email,
            "tx_ref": payment_ref,
            "callback_url": f"{settings.BASE_URL}/api/payments/verify/",
        }

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                "https://api.chapa.co/v1/transaction/initialize",
                headers=headers,
                data=json.dumps(payload),
                timeout=10
            )
            response_data = response.json()
            logger.info(f"Chapaa initiation response: {response_data}")

            if response.status_code == 200 and response_data.get("status") == "success":
                payment = Payment.objects.create(
                    user=request.user,
                    provider="chapaa",
                    amount=amount,
                    currency=currency,
                    transaction_id=response_data["data"]["tx_ref"],
                    description=description,
                    metadata=metadata,
                    status="pending",
                    payment_type=payment_type
                )
                return Response({
                    "payment": PaymentSerializer(payment).data,
                    "payment_url": response_data["data"]["checkout_url"]
                }, status=status.HTTP_201_CREATED)

            return Response({"error": "Payment initiation failed"}, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException as e:
            logger.error(f"Chapaa request error: {str(e)}")
            return Response({"error": "Payment initiation failed"}, status=status.HTTP_400_BAD_REQUEST)

    # -------------------------
    # Verify Payment
    # -------------------------
    @swagger_auto_schema(
        methods=['post'],
        request_body=PaymentVerifySerializer,
        responses={200: PaymentSerializer},
        operation_description="Verify a Chapaa payment by transaction ID",
        security=[{"Bearer": []}]
    )
    @action(detail=False, methods=['post'], url_path='verify')
    def verify(self, request):
        serializer = PaymentVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.validated_data["payment_instance"]

        try:
            response = requests.get(
                f"https://api.chapa.co/v1/transaction/verify/{payment.transaction_id}",
                headers={"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"},
                timeout=10
            )
            response_data = response.json()
            logger.info(f"Chapaa verify response: {response_data}")

            if response.status_code == 200 and response_data.get("status") == "success":
                payment.status = "completed"
                payment.save()
                return Response({"status": "completed", "payment": PaymentSerializer(payment).data})

            payment.status = "failed"
            payment.save()
            return Response({"status": "failed", "payment": PaymentSerializer(payment).data},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Chapaa verification error: {str(e)}")
            return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)

    # -------------------------
    # List Verified Payments
    # -------------------------
    @swagger_auto_schema(
        methods=['get'],
        responses={200: PaymentSerializer(many=True)},
        operation_description="List all completed Chapaa payments for the logged-in user",
        security=[{"Bearer": []}]
    )
    @action(detail=False, methods=['get'], url_path='verified')
    def verified(self, request):
        payments = Payment.objects.filter(user=request.user, provider="chapaa", status="completed")
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
