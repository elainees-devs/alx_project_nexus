# jobsboard/jobs/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Skill, Job, JobSkill
from .serializers import SkillSerializer, JobSerializer, JobSkillSerializer


class SkillAPIView(APIView):
    def get(self, request):
        skills = Skill.objects.all()
        serializer = SkillSerializer(skills, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SkillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        skill = get_object_or_404(Skill, pk=pk)
        serializer = SkillSerializer(skill, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        skill = get_object_or_404(Skill, pk=pk)
        skill.delete()
        return Response({"message": "Skill deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class JobAPIView(APIView):
    def get(self, request):
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        serializer = JobSerializer(job, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        job.delete()
        return Response({"message": "Job deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class JobSkillAPIView(APIView):
    """
    API view for creating, listing, and deleting JobSkill relationships.
    """

    def get(self, request):
        job_skills = JobSkill.objects.all()
        serializer = JobSkillSerializer(job_skills, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = JobSkillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        job_skill = get_object_or_404(JobSkill, pk=pk)
        job_skill.delete()
        return Response({"message": "JobSkill deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
