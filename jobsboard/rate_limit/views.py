# jobsboard/rate_limit/views.py
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from companies.models import Company, Industry
from .services import check_rate_limit, RateLimitExceeded
from jobs.models import Job
from .permissions import IsCompanyOwner, IsJobOwner

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# RateLimitViewSet
# ---------------------------------------------------------
# API endpoint for managing rate-limited actions.
# - Enforces rate limits on user actions such as creating or deleting jobs.
# - Attaches custom permissions depending on the action:
#    - create_job → user must be authenticated and company owner.
#    - delete_job → user must be authenticated and job owner.
# - Returns appropriate responses when limits are exceeded (HTTP 429).
# - Logs activity for auditing and debugging purposes.

class RateLimitViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Attach custom permissions depending on the action.
        """
        if self.action == "create_job":
            return [IsAuthenticated(), IsCompanyOwner()]
        elif self.action == "delete_job":
            return [IsAuthenticated(), IsJobOwner()]
        return [IsAuthenticated()]

    @swagger_auto_schema(security=[{"Bearer": []}])
    @action(detail=False, methods=["post"], url_path="create_job")
    def create_job(self, request):
        try:
            check_rate_limit(request.user, "create_job", limit=3, period_seconds=60)
        except RateLimitExceeded as e:
            logger.warning(f"Rate limit exceeded for user {request.user} on create_job. Retry after {e} seconds")
            return Response(
                {"error": f"Rate limit exceeded. Retry after {e} seconds."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        company = Company.objects.filter(owner=request.user).first()
        if not company:
            industry, _ = Industry.objects.get_or_create(name="Unknown")
            company = Company.objects.create(
                name="Default Company",
                owner=request.user,
                industry=industry,
            )
            logger.info(f"Default company created for user {request.user}")

        job = Job.objects.create(
            title=request.data.get("title", "Untitled Job"),
            description=request.data.get("description", ""),
            created_by=request.user,
            company=company,
        )
        logger.info(f"Job {job.id} created by {request.user} in company {company.name}")

        return Response(
            {
                "status": "Job created successfully",
                "job_id": job.id,
                "title": job.title,
                "company": company.name,
            },
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(security=[{"Bearer": []}])
    @action(detail=True, methods=["delete"], url_path="delete_job")
    def delete_job(self, request, pk=None):
        try:
            check_rate_limit(request.user, "delete_job", limit=3, period_seconds=60)
        except RateLimitExceeded as e:
            logger.warning(f"Rate limit exceeded for user {request.user} on delete_job. Retry after {e} seconds")
            return Response(
                {"error": f"Rate limit exceeded. Retry after {e} seconds."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        try:
            job = Job.objects.get(id=pk)
            self.check_object_permissions(request, job)
            job.delete()
            logger.info(f"Job {pk} deleted by {request.user}")
        except Job.DoesNotExist:
            logger.error(f"User {request.user} tried to delete non-existent job {pk}")
            return Response(
                {"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"status": f"Job {pk} deleted successfully"},
            status=status.HTTP_200_OK,
        )
