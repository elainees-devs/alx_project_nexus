# jobsboard/analytics/models.py
from django.db import models
from jobs.models import Job
from django.contrib.auth import get_user_model

User = get_user_model()

class JobViewAggregate(models.Model):
    """
    Stores daily aggregates of job views for faster analytics queries.
    """
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='view_aggregates'
    )
    date = models.DateField()  # The day the views were counted
    view_count = models.PositiveIntegerField(default=0)
    computed_at = models.DateTimeField(auto_now_add=True)  # When the aggregate was created/updated

    class Meta:
        unique_together = ('job', 'date')
        indexes = [
            models.Index(fields=['job'], name='idx_job_aggregate_job'),
            models.Index(fields=['date'], name='idx_job_aggregate_date'),
        ]
        ordering = ['-date']  # Returns newest first by default

    def __str__(self):
        return f"{self.job.title} - {self.date}: {self.view_count} views"


class JobApplicationAggregate(models.Model):
    """
    Stores daily aggregates of job applications for analytics.
    """
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='application_aggregates'
    )
    date = models.DateField()
    application_count = models.PositiveIntegerField(default=0)
    computed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'date')
        indexes = [
            models.Index(fields=['job'], name='idx_job_app_aggregate_job'),
            models.Index(fields=['date'], name='idx_job_app_aggregate_date'),
        ]
        ordering = ['-date']

    def __str__(self):
        return f"{self.job.title} - {self.date}: {self.application_count} applications"
