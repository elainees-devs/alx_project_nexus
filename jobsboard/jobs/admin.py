# jobsboard/jobs/admin.py
from django.contrib import admin
from .models import Job, Skill, JobSkill

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'company', 'employment_type', 'work_location_type', 'experience_level', 'status', 'posted_date', 'closing_date')
    list_filter = ('employment_type', 'work_location_type', 'experience_level', 'status', 'company')
    search_fields = ('title', 'description', 'location', 'company__name')
    date_hierarchy = 'posted_date'
    filter_horizontal = ('skills',)

@admin.register(JobSkill)
class JobSkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'skill')
    search_fields = ('job__title', 'skill__name')
