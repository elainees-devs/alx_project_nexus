import logging
from rest_framework import viewsets, permissions, status
from django_filters import rest_framework as django_filters
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Application, ApplicationFile
from .serializers import ApplicationSerializer, ApplicationFileSerializer

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# ApplicationViewSet
# ---------------------------------------------------------
# Handles job application logic:
# - Seekers can create applications (with IP tracking).
# - Prevents duplicate applications to the same job.
# - Recruiters can view/update applications for their jobs.
# - Seekers can only see their own applications.
# - Admins can view and manage all applications.
# Includes filtering, searching, ordering, and role-based restrictions.
class ApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing job applications."""
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Filtering, searching, ordering
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["job", "status", "applicant"]
    search_fields = ["job__title", "applicant__username"]
    ordering_fields = ["applied_at", "status"]  
    ordering = ["-applied_at"]

    def perform_create(self, serializer):
        """Attach applicant and IP address when seeker creates an application."""
        application = serializer.save(
            applicant=self.request.user,
            ip_address=self.get_client_ip(),
        )
        logger.info(f"Application {application.id} created by {self.request.user} from IP {application.ip_address}")

    def get_client_ip(self):
        """Get client IP from request headers safely."""
        x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
        return x_forwarded_for.split(",")[0].strip() if x_forwarded_for else self.request.META.get("REMOTE_ADDR")

    def get_queryset(self):
        """Limit visibility depending on user role."""
        qs = super().get_queryset()
        user = self.request.user

        if getattr(user, "role", None) == "SEEKER":
            logger.debug(f"Seeker {user} fetching own applications")
            return qs.filter(applicant=user)

        elif getattr(user, "role", None) == "RECRUITER":
            logger.debug(f"Recruiter {user} fetching applications for owned jobs")
            return qs.filter(job__company__owner=user)

        logger.debug(f"Admin {user} fetching all applications")
        return qs

    def create(self, request, *args, **kwargs):
        """Prevent duplicate applications for the same job by the same seeker."""
        if getattr(request.user, "role", None) != "SEEKER":
            logger.warning(f"Unauthorized create attempt by {request.user} (role={getattr(request.user, 'role', None)})")
            raise PermissionDenied("Only job seekers can apply for jobs.")

        job_id = request.data.get("job")
        if job_id and Application.objects.filter(job_id=job_id, applicant=request.user).exists():
            logger.warning(f"Duplicate application attempt by {request.user} for job {job_id}")
            return Response(
                {"error": "You have already applied to this job."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Restrict who can update applications:
        - Seekers cannot change status.
        - Recruiters can only update status or review fields.
        - Admins can update everything.
        """
        user = request.user
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        if getattr(user, "role", None) == "SEEKER":
            if any(field in request.data for field in ["status", "reviewed_by", "reviewed_at"]):
                logger.error(f"Seeker {user} attempted unauthorized status/review update on Application {instance.id}")
                raise PermissionDenied("You cannot change status or review fields.")

        elif getattr(user, "role", None) == "RECRUITER":
            allowed_fields = {"status", "reviewed_by", "reviewed_at"}
            if not set(request.data.keys()).issubset(allowed_fields): 
                logger.error(f"Recruiter {user} attempted unauthorized update on Application {instance.id}")
                raise PermissionDenied("Recruiters can only update status or review fields.")

        elif not user.is_superuser:
            logger.error(f"Unauthorized update attempt by {user} on Application {instance.id}")
            raise PermissionDenied("You don't have permission to update this application.")

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        logger.info(f"Application {instance.id} updated by {user}")
        return Response(serializer.data)


# ---------------------------------------------------------
# ApplicationFileViewSet
# ---------------------------------------------------------
# Handles application file uploads and management:
# - Seekers can upload files (e.g., CV, cover letter) for their own applications.
# - Recruiters can view files attached to applications for their jobs.
# - Admins can view/manage all files.
# Includes role-based access restrictions and validation.
class ApplicationFileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing application files."""
    queryset = ApplicationFile.objects.all()
    serializer_class = ApplicationFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["application", "file_type"]
    search_fields = ["application__job__title", "application__applicant__username"]
    ordering_fields = ["uploaded_at"]
    ordering = ["-uploaded_at"]

    def get_queryset(self):
        """Limit file access depending on user role."""
        user = self.request.user

        if getattr(user, "role", None) == "SEEKER":
            logger.debug(f"Seeker {user} fetching own application files")
            return self.queryset.filter(application__applicant=user)

        elif getattr(user, "role", None) == "RECRUITER":
            logger.debug(f"Recruiter {user} fetching application files for owned jobs")
            return self.queryset.filter(application__job__company__owner=user)

        logger.debug(f"Admin {user} fetching all application files")
        return self.queryset

    def create(self, request, *args, **kwargs):
        """Attach files to an application (seekers only)."""
        if getattr(request.user, "role", None) != "SEEKER":
            logger.warning(f"Unauthorized file upload attempt by {request.user}")
            raise PermissionDenied("Only seekers can upload application files.")

        application_id = request.data.get("application")
        if not application_id:
            logger.error(f"File upload failed by {request.user}: missing application_id")
            return Response(
                {"error": "Application ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            application = Application.objects.get(id=application_id, applicant=request.user)
        except Application.DoesNotExist:
            logger.error(f"File upload failed by {request.user}: invalid application {application_id}")
            return Response(
                {"error": "Application not found or you don't have permission."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file_instance = serializer.save(application=application)
        logger.info(f"File {file_instance.id} uploaded by {request.user} for Application {application_id}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
