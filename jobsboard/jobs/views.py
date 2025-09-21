# jobsboard/jobs/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .permissions import JobPermission
from .models import Skill, Job, JobSkill
from users.models import User
from .filters import JobFilter
from .serializers import SkillSerializer, JobSerializer, JobSkillSerializer


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

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "employment_type", openapi.IN_QUERY,
                description="Employment type",
                type=openapi.TYPE_STRING,
                enum=[choice[0] for choice in Job.EMPLOYMENT_TYPE_CHOICES],
            ),
            openapi.Parameter(
                "work_location_type", openapi.IN_QUERY,
                description="Work location type",
                type=openapi.TYPE_STRING,
                enum=[choice[0] for choice in Job.WORK_LOCATION_TYPE_CHOICES],
            ),
            openapi.Parameter(
                "experience_level", openapi.IN_QUERY,
                description="Experience level",
                type=openapi.TYPE_STRING,
                enum=[choice[0] for choice in Job.EXPERIENCE_LEVEL_CHOICES],
            ),
            openapi.Parameter(
                "status", openapi.IN_QUERY,
                description="Job status",
                type=openapi.TYPE_STRING,
                enum=[choice[0] for choice in Job.JOB_STATUS_CHOICES],
            ),
            openapi.Parameter(
                "location", openapi.IN_QUERY,
                description="Filter by job location (city or country)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "min_salary", openapi.IN_QUERY,
                description="Minimum salary",
                type=openapi.TYPE_NUMBER,
                format=openapi.FORMAT_DECIMAL,
            ),
            openapi.Parameter(
                "max_salary", openapi.IN_QUERY,
                description="Maximum salary",
                type=openapi.TYPE_NUMBER,
                format=openapi.FORMAT_DECIMAL,
            ),
            openapi.Parameter(
                "ordering", openapi.IN_QUERY,
                description="Order results by `salary_min`, `salary_max`, or `posted_date` (prefix with `-` for descending)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "search", openapi.IN_QUERY,
                description="Search jobs by title, company name, or description",
                type=openapi.TYPE_STRING,
            ),
        ],
        security=[{"Bearer": []}]
    )
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

    # -----------------------------
    # Apply action (Job Seekers only)
    # -----------------------------
    @swagger_auto_schema(security=[{"Bearer": []}])
    @action(detail=True, methods=["post"], url_path="apply", permission_classes=[IsAuthenticated])
    def apply(self, request, pk=None):
        """
        Allow job seekers to apply for a job.
        """
        job = self.get_object()

        # Role check
        if request.user.role != User.ROLE_SEEKER:
            raise PermissionDenied("Only job seekers can apply for jobs.")

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
