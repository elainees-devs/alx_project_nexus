# jobsboard/jobs/serializers.py
from django.shortcuts import render
from rest_framework import serializers
from .models import Skill,Job, JobSkill

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model=Skill
        fields="__all__"
class JobSerializer(serializers.ModelSerializer):
    industry=serializers.CharField(source="company.industry.name", read_only=True)

    class Meta:
        model=Job
        fields="__all__"


class JobSkillSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)
    skill_name = serializers.CharField(source="skill.name", read_only=True)

    class Meta:
        model = JobSkill
        fields = ['id', 'job', 'job_title', 'skill', 'skill_name']
        read_only_fields = ['id', 'job_title', 'skill_name']