# jobsboard/notifications/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import Notification
from .permissions import NotificationPermission
from .serializers import NotificationSerializer, NotificationCreateSerializer


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
        user = self.request.user

        # Admin sees everything
        if user.is_staff or user.is_admin:
            return Notification.objects.all()

        # Employer → notifications of seekers in their company/companies
        if user.is_recruiter:
            companies = user.companies.all()
            return Notification.objects.filter(user__company__in=companies)

        # Seeker → only their own notifications
        if user.is_seeker:
            return Notification.objects.filter(user=user)

        return Notification.objects.none()



    def get_serializer_class(self):
        if self.action == "create":
            return NotificationCreateSerializer
        return NotificationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(security=[{"Bearer": []}])
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().order_by("-created_at")
        self.queryset = queryset
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(security=[{"Bearer": []}])
    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "read"}, status=status.HTTP_200_OK)
