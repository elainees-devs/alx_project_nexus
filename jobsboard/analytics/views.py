#jobsboard/analytics/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from django.db.models import Count

from jobs.models import Job
from applications.models import Application 
from .models import JobViewAggregate, JobApplicationAggregate
from .serializers import JobViewAggregateSerializer, JobApplicationAggregateSerializer


class JobViewAggregateViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("start_date", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("end_date", openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ],
        responses={200: JobViewAggregateSerializer(many=True)},
        security=[{"Bearer": []}],
    )
    @action(detail=False, methods=["get"], url_path="job-views")
    def list_views(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        queryset = JobViewAggregate.objects.all()
        if not request.user.is_superuser:
            queryset = queryset.filter(job__created_by=request.user)

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        queryset = queryset.order_by("-date")
        serializer = JobViewAggregateSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class JobApplicationAggregateViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("start_date", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("end_date", openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ],
        responses={200: JobApplicationAggregateSerializer(many=True)},
        security=[{"Bearer": []}],
    )
    @action(detail=False, methods=["get"], url_path="job-applications")
    def list_applications(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        applications = Application.objects.all()
        if not request.user.is_superuser:
            applications = applications.filter(job__created_by=request.user)

        # Date filtering based on applied_at
        if start_date:
            applications = applications.filter(applied_at__date__gte=start_date)
        if end_date:
            applications = applications.filter(applied_at__date__lte=end_date)

        # Aggregate by job and date of application
        aggregated = applications.values(
            "job", "job__title", "job__company__name", "applied_at__date"
        ).annotate(application_count=Count("id")).order_by("-application_count")

        for item in aggregated:
            JobApplicationAggregate.objects.update_or_create(
                job_id=item["job"],
                date=item["applied_at__date"], 
                defaults={"application_count": item["application_count"]},
            )

        # Return queryset filtered by user
        queryset = JobApplicationAggregate.objects.all()
        if not request.user.is_superuser:
            queryset = queryset.filter(job__created_by=request.user)

        serializer = JobApplicationAggregateSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
