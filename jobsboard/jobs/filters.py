#jobsboard/jobs/filters.py
import django_filters
from .models import Job

class JobFilter(django_filters.FilterSet):
    # Numeric filters for salary
    min_salary = django_filters.NumberFilter(field_name="salary_min", lookup_expr="gte")
    max_salary = django_filters.NumberFilter(field_name="salary_max", lookup_expr="lte")

    # Filters for choice fields (enums)
    employment_type = django_filters.ChoiceFilter(choices=Job.EMPLOYMENT_TYPE_CHOICES)
    work_location_type = django_filters.ChoiceFilter(choices=Job.WORK_LOCATION_TYPE_CHOICES)
    experience_level = django_filters.ChoiceFilter(choices=Job.EXPERIENCE_LEVEL_CHOICES)
    status = django_filters.ChoiceFilter(choices=Job.JOB_STATUS_CHOICES)

    # Text search for location
    location = django_filters.CharFilter(field_name="location", lookup_expr="icontains")
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    industry = django_filters.CharFilter(field_name="industry__name", lookup_expr="icontains")  # if using ForeignKey to Industry


    class Meta:
        model = Job
        fields = [
            "employment_type",
            "work_location_type",
            "experience_level",
            "status",
            "location",
            "min_salary",
            "max_salary",
            "title",
            "industry"
        ]

