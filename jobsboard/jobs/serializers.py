from django.shortcuts import render
from rest_framework import serializers

from .models import Skill, Job, JobSkill


# ---------------------------------------------------------
# SkillSerializer
# ---------------------------------------------------------
# Serializes Skill model data.
# - Exposes all fields of the Skill model.
# - Used for creating, updating, and retrieving skills.
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"


# ---------------------------------------------------------
# JobSerializer
# ---------------------------------------------------------
# Serializes Job model data.
# - Includes all job fields from the model.
# - Adds a read-only `industry` field sourced from the related company's industry.
class JobSerializer(serializers.ModelSerializer):
    industry = serializers.CharField(source="company.industry.name", read_only=True)

    class Meta:
        model = Job
        fields = "__all__"


# ---------------------------------------------------------
# JobSkillSerializer
# ---------------------------------------------------------
# Serializes the JobSkill intermediate model (many-to-many relation).
# - Includes job and skill IDs.
# - Adds read-only job title and skill name for human-readable output.
# - Useful for linking jobs with their required skills.
class JobSkillSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)
    skill_name = serializers.CharField(source="skill.name", read_only=True)

    class Meta:
        model = JobSkill
        fields = ['id', 'job', 'job_title', 'skill', 'skill_name']
        read_only_fields = ['id', 'job_title', 'skill_name']
