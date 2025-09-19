# jobsboard/rate_limit/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from jobs.models import Job
from companies.models import Company, Industry
from .services import check_rate_limit, RateLimitExceeded
from drf_yasg.utils import swagger_auto_schema


class RateLimitViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(security=[{"Bearer": []}])
    @action(detail=False, methods=["post"], url_path="create_job")
    def create_job(self, request):
        try:
            # Check rate limit for this action
            check_rate_limit(request.user, "create_job", limit=3, period_seconds=60)
        except RateLimitExceeded as e:
            return Response(
                {"error": f"Rate limit exceeded. Retry after {e} seconds."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Ensure user has a company
        company = Company.objects.filter(owner=request.user).first()
        if not company:
            # Create a default industry if none exists
            industry, _ = Industry.objects.get_or_create(name="Unknown")
            company = Company.objects.create(
                name="Default Company",
                owner=request.user,
                industry=industry,
            )

        # Create the job
        job = Job.objects.create(
            title=request.data.get("title", "Untitled Job"),
            description=request.data.get("description", ""),
            created_by=request.user,
            company=company
        )

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
            # Check rate limit for this action
            check_rate_limit(request.user, "delete_job", limit=3, period_seconds=60)
        except RateLimitExceeded as e:
            return Response(
                {"error": f"Rate limit exceeded. Retry after {e} seconds."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Delete the job
        try:
            job = Job.objects.get(id=pk, created_by=request.user)
            job.delete()
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {"status": f"Job {pk} deleted successfully"},
            status=status.HTTP_200_OK,
        )
