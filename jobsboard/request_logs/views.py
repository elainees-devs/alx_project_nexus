# jobsboard/request_logs/views.py
import logging
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import RequestLog
from .serializers import RequestLogSerializer

logger = logging.getLogger(__name__)


class RequestLogViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for request logs:
    - list (all logs for user)
    - retrieve (single log)
    - create log (custom)
    """
    serializer_class = RequestLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = RequestLog.objects.all()

    # Users only see their own logs
    def get_queryset(self):
        return RequestLog.objects.filter(user=self.request.user)

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
    # Custom Action: Log Request
    # -------------------------
    @swagger_auto_schema(
        methods=['post'],
        request_body=RequestLogSerializer,
        responses={201: RequestLogSerializer},
        operation_description="Manually create a request log entry",
        security=[{"Bearer": []}]
    )
    @action(detail=False, methods=['post'], url_path='log')
    def log_request(self, request):
        serializer = RequestLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        logger.info(f"Request logged for user {request.user}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
