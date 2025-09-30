import uuid
import requests
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.urls import reverse
from drf_yasg.utils import swagger_auto_schema

from users.models import User
from .models import Payment
from .serializers import PaymentInputSerializer, PaymentSerializer
from .services.chapa import ChapaAPI

# ---------------------------------------------------------
# PaymentViewSet
# ---------------------------------------------------------
# API endpoint for managing payments.
# - Authenticated users can view their own payments.
# - Admins can view all payments.
# - Provides endpoints to:
#    - Initiate a payment via Chapa API (`initiate_payment`)
#    - Verify a payment transaction (`verify_payment`)
#    - Handle payment callbacks (`payments_callback`)
# - Enforces authentication and integrates with the Payment model and serializers.
# - Handles validation, defaults, and error handling for payment initiation.

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_staff or user.role == User.ROLE_ADMIN):
            return Payment.objects.all()
        if user.is_authenticated:
            return Payment.objects.filter(user=user)
        return Payment.objects.none()

    @swagger_auto_schema(
        method='post',
        request_body=PaymentInputSerializer,
        responses={201: PaymentSerializer}
    )
    @action(detail=False, methods=["post"], url_path="initiate", permission_classes=[IsAuthenticated])
    def initiate_payment(self, request):
        serializer = PaymentInputSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            chapa = ChapaAPI()

            # Ensure tx_ref exists
            tx_ref = data.get("tx_ref") or f"jobplatform-{uuid.uuid4()}"

            callback_url = data.get("callback_url") or request.build_absolute_uri(reverse("payments-callback"))
            return_url = data.get("return_url") or "https://example.com/"

            # Provide defaults for optional fields
            email = data.get("email") or getattr(request.user, "email", "guest@example.com")
            first_name = data.get("first_name") or getattr(request.user, "first_name", "Guest")
            last_name = data.get("last_name") or getattr(request.user, "last_name", "User")
            phone_number = data.get("phone_number") or "0912345678"
            customization = data.get("customization") or {
                "title": f"Payment for {data['payment_type']}",
                "description": data.get("description", "")
            }

            try:
                # Initialize payment via Chapa
                response = chapa.initialize_payment(
                    amount=str(data["amount"]),
                    currency=data.get("currency", "ETB"),
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    tx_ref=tx_ref,
                    callback_url=callback_url,
                    return_url=return_url,
                    customization=customization
                )
            except requests.exceptions.HTTPError as e:
                return Response({"error": "Chapa API error", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # Save payment locally
            payment = Payment.objects.create(
                user=request.user,
                amount=data["amount"],
                currency=data.get("currency", "ETB"),
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                tx_ref=tx_ref,
                callback_url=callback_url,
                return_url=return_url,
                customization=customization
            )

            return Response({
                "checkout_url": response["data"]["checkout_url"],
                "payment": PaymentSerializer(payment).data
            }, status=status.HTTP_201_CREATED)

        # If serializer is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="verify")
    def verify_payment(self, request, pk=None):
        payment = self.get_object()
        chapa = ChapaAPI()
        verification = chapa.verify_payment(payment.tx_ref)

        return Response({
            "verification": verification,
            "payment": PaymentSerializer(payment).data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="callback", url_name="payments-callback")
    def payments_callback(self, request):
        tx_ref = request.data.get("tx_ref")
        try:
            payment = Payment.objects.get(tx_ref=tx_ref)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        chapa = ChapaAPI()
        verification = chapa.verify_payment(tx_ref)

        return Response({"message": "Callback processed", "verification": verification})
