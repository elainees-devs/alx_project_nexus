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
    """
    Request logs viewset:
    - Normal users: can view their own logs
    - Admins: can view/manage all logs
    """
    serializer_class = RequestLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = RequestLog.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return RequestLog.objects.all()
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
