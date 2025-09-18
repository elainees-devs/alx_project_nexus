# jobsboard/jobs/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SkillViewSet, JobViewSet, JobSkillViewSet

router = DefaultRouter()
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'job-skills', JobSkillViewSet, basename='jobskill')

urlpatterns = [
    path("", include(router.urls)),
]
