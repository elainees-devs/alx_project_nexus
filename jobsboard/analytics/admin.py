# jobsboard/analytics/admin.py
from django.contrib import admin
from .models import JobViewAggregate, JobApplicationAggregate

# ----------------------------
# JobViewAggregate Admin
# ----------------------------
@admin.register(JobViewAggregate)
class JobViewAggregateAdmin(admin.ModelAdmin):
    """Admin configuration for JobViewAggregate model."""
    list_display = ("id", "job", "date", "view_count", "computed_at")
    list_filter = ("date", "job")
    search_fields = ("job__title", "job__company__name")
    ordering = ("-date",)


# ----------------------------
# JobApplicationAggregate Admin
# ----------------------------
@admin.register(JobApplicationAggregate)
class JobApplicationAggregateAdmin(admin.ModelAdmin):
    """Admin configuration for JobApplicationAggregate model."""
    list_display = ("id", "job", "date", "application_count", "computed_at")
    list_filter = ("date", "job")
    search_fields = ("job__title", "job__company__name")
    ordering = ("-date",)

