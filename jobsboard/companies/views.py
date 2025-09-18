#jobsboard/companies/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .models import Industry, Company
from .serializers import IndustrySerializer, CompanySerializer


# -----------------------------
# Industry ViewSet
# -----------------------------
class IndustryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing industries.
    """
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer

    # Public GET, others require authentication
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

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


# -----------------------------
# Company ViewSet
# -----------------------------
class CompanyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing companies.
    Requires JWT authentication.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    # Automatically set owner to request.user on creation
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # Swagger security annotations
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
