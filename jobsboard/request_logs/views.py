# jobsboard/request_logs/views.py
import logging
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import RequestLog
from .serializers import RequestLogSerializer
from .permissions import IsOwnerOrAdmin

logger = logging.getLogger(__name__)


class RequestLogViewSet(viewsets.ModelViewSet):
    serializer_class = RequestLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Safe for Swagger/OpenAPI schema generation
        if getattr(self, "swagger_fake_view", False):
            return RequestLog.objects.none()

        user = self.request.user
        if not user.is_authenticated:
            return RequestLog.objects.none()

        # Users only see their own logs
        return RequestLog.objects.filter(user=user)



    def has_admin_rights(self, request):
        return request.user.is_staff or request.user.is_superuser

    # -------------------------
    # CRUD Permissions
    # -------------------------
    @swagger_auto_schema(security=[{"Bearer": []}])
    def update(self, request, *args, **kwargs):
        if not self.has_admin_rights(request):
            return Response(
                {"detail": "Only admins can update logs."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(security=[{"Bearer": []}])
    def partial_update(self, request, *args, **kwargs):
        if not self.has_admin_rights(request):
            return Response(
                {"detail": "Only admins can update logs."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(security=[{"Bearer": []}])
    def destroy(self, request, *args, **kwargs):
        if not self.has_admin_rights(request):
            return Response(
                {"detail": "Only admins can delete logs."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)
