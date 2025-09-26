# jobsboard/jobs/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from .permissions import JobPermission
from .models import Skill, Job, JobSkill
from users.models import User
from .filters import JobFilter
from .serializers import SkillSerializer, JobSerializer, JobSkillSerializer

logger = logging.getLogger(__name__)

# -----------------------------
# Skill ViewSet
# -----------------------------
class SkillViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing skills.
    Public can view, only recruiters/admins can create/update/delete.
    """
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [JobPermission]

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
# Job ViewSet
# -----------------------------
class JobViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing jobs.
    - Public: can view jobs
    - Job Seekers: can view + apply
    - Recruiters/Admins: full CRUD
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [JobPermission]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JobFilter
    search_fields = ["title", "company__name", "description"]
    ordering_fields = ["salary_min", "salary_max", "posted_date"]

    def get_permissions(self):
        # Allow Swagger to see POST endpoint
        if getattr(self, '_swagger_fake_view', False):
            return [AllowAny()]
        return super().get_permissions()

    # -----------------------------
    # Swagger parameters for filtering
    # -----------------------------
    title_param = openapi.Parameter(
        'title', openapi.IN_QUERY,
        description="Filter jobs by title (case-insensitive, partial match)",
        type=openapi.TYPE_STRING
    )
    industry_param = openapi.Parameter(
        'industry', openapi.IN_QUERY,
        description="Filter jobs by industry name (case-insensitive, partial match)",
        type=openapi.TYPE_STRING
    )
    min_salary_param = openapi.Parameter(
        'min_salary', openapi.IN_QUERY,
        description="Filter jobs with minimum salary greater than or equal to this value",
        type=openapi.TYPE_NUMBER
    )
    max_salary_param = openapi.Parameter(
        'max_salary', openapi.IN_QUERY,
        description="Filter jobs with maximum salary less than or equal to this value",
        type=openapi.TYPE_NUMBER
    )
    status_param = openapi.Parameter(
        'status', openapi.IN_QUERY,
        description="Filter jobs by status (open, closed, draft)",
        type=openapi.TYPE_STRING
    )



    @swagger_auto_schema(security=[{"Bearer": []}])
    def create(self, request, *args, **kwargs):
        logger.info(f"User {request.user} is creating a job")
        try:
            response = super().create(request, *args, **kwargs)
            logger.info(f"Job created successfully by {request.user}")
            return response
        except Exception as e:
            logger.error(f"Error creating job by {request.user}: {str(e)}", exc_info=True)
            raise

    @swagger_auto_schema(security=[{"Bearer": []}])
    @action(detail=True, methods=["post"], url_path="apply", permission_classes=[IsAuthenticated])
    def apply(self, request, pk=None):
        """
        Allow job seekers to apply for a job.
        """
        job = self.get_object()

        # Role check
        if request.user.role != User.ROLE_SEEKER:
            logger.warning(f"Permission denied: {request.user} tried to apply for job {job.id}")
            raise PermissionDenied("Only job seekers can apply for jobs.")

        logger.info(f"User {request.user.username} is applying for job {job.id} - {job.title}")

        # Example: saving application (future)
        # JobApplication.objects.create(user=request.user, job=job)

        return Response(
            {"message": f"User {request.user.username} applied for {job.title}"},
            status=status.HTTP_201_CREATED,
        )



# -----------------------------
# JobSkill ViewSet
# -----------------------------
class JobSkillViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Job-Skill relationships.
    Public can view, recruiters/admins manage.
    """
    queryset = JobSkill.objects.all()
    serializer_class = JobSkillSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [JobPermission]

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
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
