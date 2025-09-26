# jobsboard/companies/views.py
import logging
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Industry, Company
from .serializers import IndustrySerializer, CompanySerializer

logger = logging.getLogger(__name__)


# -----------------------------
# Industry ViewSet
# -----------------------------
class IndustryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing industries.
    """
    queryset = Industry.objects.all().order_by("id")
    serializer_class = IndustrySerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        elif self.action == 'destroy':  # DELETE only for admins
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @swagger_auto_schema(security=[{"Bearer": []}])
    def create(self, request, *args, **kwargs):
        name = request.data.get("name", "").strip()
        if not name:
            return Response({"error": "Name is required"}, status=status.HTTP_400_BAD_REQUEST)

        industry, created = Industry.objects.get_or_create(name=name)

        if not created:
            return Response(
                {"warning": f"Industry '{name}' already exists.", "id": industry.id},
                status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(industry)
        logger.info(f"Industry created by {request.user}: {serializer.data}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(security=[{"Bearer": []}])
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        logger.info(f"Industry updated by {request.user}: {response.data}")
        return response

    @swagger_auto_schema(security=[{"Bearer": []}])
    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        logger.info(f"Industry partially updated by {request.user}: {response.data}")
        return response

    @swagger_auto_schema(security=[{"Bearer": []}])
    def destroy(self, request, *args, **kwargs):
        industry = self.get_object()
        logger.warning(f"Industry {industry.id} deleted by {request.user}")
        return super().destroy(request, *args, **kwargs)


# -----------------------------
# Company Permissions
# -----------------------------
class IsEmployerOrAdmin(permissions.BasePermission):
    """
    Custom permission:
    - Employers and admins can create/update
    - Admins only can delete
    """

    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return True

        if request.user and request.user.is_staff:
            return True

        if view.action in ['create', 'update', 'partial_update']:
            return getattr(request.user, "role", None) == "employer"

        if view.action == 'destroy':
            return request.user and request.user.is_staff

        return False


# -----------------------------
# Company ViewSet
# -----------------------------
class CompanyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing companies.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsEmployerOrAdmin]

    def perform_create(self, serializer):
        company = serializer.save(owner=self.request.user)
        logger.info(f"Company created by {self.request.user}: {company}")

    @swagger_auto_schema(security=[{"Bearer": []}])
    def list(self, request, *args, **kwargs):
        logger.debug(f"Company list requested by {request.user}")
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(security=[{"Bearer": []}])
    def retrieve(self, request, *args, **kwargs):
        logger.debug(f"Company retrieve requested by {request.user}")
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(security=[{"Bearer": []}])
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        logger.info(f"Company created by {request.user}: {response.data}")
        return response

    @swagger_auto_schema(security=[{"Bearer": []}])
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        logger.info(f"Company updated by {request.user}: {response.data}")
        return response

    @swagger_auto_schema(security=[{"Bearer": []}])
    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        logger.info(f"Company partially updated by {request.user}: {response.data}")
        return response

    @swagger_auto_schema(security=[{"Bearer": []}])
    def destroy(self, request, *args, **kwargs):
        company = self.get_object()
        logger.warning(f"Company {company.id} deleted by {request.user}")
        return super().destroy(request, *args, **kwargs)
