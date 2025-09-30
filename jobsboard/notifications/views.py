# jobsboard/notifications/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema

from .models import Notification
from .permissions import NotificationPermission
from .serializers import NotificationSerializer, NotificationCreateSerializer

# ---------------------------------------------------------
# NotificationViewSet
# ---------------------------------------------------------
# API endpoint for managing user notifications.
# - Admin: can see all notifications.
# - Employer/Recruiter: can see notifications of job seekers in their company/companies.
# - Job seeker: can see only their own notifications.
# - Supports creating notifications (by recruiters), listing, and marking as read.
# - Enforces role-based access using NotificationPermission.
# - Integrates Swagger for API documentation.
class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing notifications.
    Admin -> sees all
    Employer -> sees their job seekers' notifications
    Job seeker -> sees only their own
    """
    queryset = Notification.objects.all()
    permission_classes = [NotificationPermission]

    def get_queryset(self):
        # Swagger schema generation uses fake view
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()

        user = self.request.user
        if not user.is_authenticated:
            return Notification.objects.none()

        # Admin sees everything
        if user.is_staff or getattr(user, "is_admin", False):
            return Notification.objects.all().order_by("-created_at")

        # Employer → notifications of seekers in their company/companies
        if getattr(user, "is_recruiter", False):
            companies = user.companies.all()
            return Notification.objects.filter(user__company__in=companies).order_by("-created_at")

        # Seeker → only their own notifications
        if getattr(user, "is_seeker", False):
            return Notification.objects.filter(user=user).order_by("-created_at")

        return Notification.objects.none()

    def get_serializer_class(self):
        if self.action == "create":
            return NotificationCreateSerializer
        return NotificationSerializer

    def perform_create(self, serializer):
        user = self.request.user
        # Only recruiters can create notifications
        if not getattr(user, "is_recruiter", False):
            raise PermissionDenied("Only recruiters can create notifications")
        serializer.save(user=user)

    @swagger_auto_schema(security=[{"Bearer": []}])
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        self.queryset = queryset
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(security=[{"Bearer": []}])
    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        user = request.user

        # Ensure only owners or admins can mark as read
        if notification.user != user and not (user.is_staff or getattr(user, "is_admin", False)):
            raise PermissionDenied("You do not have permission to mark this notification as read.")

        notification.is_read = True
        notification.save()
        return Response({"status": "read"}, status=status.HTTP_200_OK)
