#jobsboard/analytics/serializers.py
from rest_framework import serializers
from .models import JobViewAggregate, JobApplicationAggregate

class JobViewAggregateSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company.name', read_only=True)

    class Meta:
        model = JobViewAggregate
        fields = ['id', 'job', 'job_title', 'company_name', 'date', 'view_count']


class JobApplicationAggregateSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company.name', read_only=True)

    class Meta:
        model = JobApplicationAggregate
        fields = ['id', 'job', 'job_title', 'company_name', 'date', 'application_count']
