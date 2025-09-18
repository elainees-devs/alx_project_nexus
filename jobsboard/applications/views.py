# jobsboard/applications/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Application, ApplicationFile
from .serializers import ApplicationSerializer, ApplicationFileSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing job applications."""
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Attach applicant and IP address when seeker creates an application."""
        serializer.save(
            applicant=self.request.user,
            ip_address=self.get_client_ip(),
        )

    def get_client_ip(self):
        """Get client IP from request headers safely."""
        x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = self.request.META.get("REMOTE_ADDR")
        return ip

    def get_queryset(self):
        """Limit visibility depending on user role."""
        qs = super().get_queryset()
        user = self.request.user

        if getattr(user, "role", None) == "SEEKER":
            # Seekers only see their own applications
            qs = qs.filter(applicant=user)

        elif getattr(user, "role", None) == "RECRUITER":
            # Recruiters only see applications for jobs in their company
            qs = qs.filter(job__company__owner=user)

        # Admins & superusers see everything by default
        return qs

    def create(self, request, *args, **kwargs):
        """Prevent duplicate applications for the same job by the same seeker."""
        if getattr(request.user, "role", None) != "SEEKER":
            raise PermissionDenied("Only job seekers can apply for jobs.")

        job_id = request.data.get("job")
        if job_id and Application.objects.filter(job_id=job_id, applicant=request.user).exists():
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
        """
        user = request.user
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        if getattr(user, "role", None) == "SEEKER":
            # Seekers can only edit their cover letter
            if "status" in request.data or "reviewed_by" in request.data or "reviewed_at" in request.data:
                raise PermissionDenied("You cannot change status or review fields.")

        elif getattr(user, "role", None) == "RECRUITER":
            # Recruiters can only update status and review-related fields
            allowed_fields = {"status", "reviewed_by", "reviewed_at"}
            if any(field not in allowed_fields for field in request.data.keys()):
                raise PermissionDenied("Recruiters can only update status or review fields.")

        elif not user.is_superuser:
            raise PermissionDenied("You don't have permission to update this application.")

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class ApplicationFileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing application files."""
    queryset = ApplicationFile.objects.all()
    serializer_class = ApplicationFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Limit file access depending on user role."""
        user = self.request.user

        if getattr(user, "role", None) == "SEEKER":
            # Seekers only see their own application files
            return self.queryset.filter(application__applicant=user)

        elif getattr(user, "role", None) == "RECRUITER":
            # Recruiters only see files for jobs they own
            return self.queryset.filter(application__job__company__owner=user)

        # Admins & superusers see all
        return self.queryset

    def create(self, request, *args, **kwargs):
        """Attach files to an application (seekers only)."""
        if getattr(request.user, "role", None) != "SEEKER":
            raise PermissionDenied("Only seekers can upload application files.")

        application_id = request.data.get("application")
        if not application_id:
            return Response(
                {"error": "Application ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            application = Application.objects.get(id=application_id, applicant=request.user)
        except Application.DoesNotExist:
            return Response(
                {"error": "Application not found or you don't have permission."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(application=application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
