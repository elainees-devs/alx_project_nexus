# jobsboard/jobs/urls.py
from django.urls import path
from .views import SkillAPIView, JobAPIView, JobSkillAPIView

urlpatterns = [
    # Skill endpoints
    path('skills/', SkillAPIView.as_view(), name='skill-list'),
    path('skills/<int:pk>/', SkillAPIView.as_view(), name='skill-detail'),

    # Job endpoints
    path('jobs/', JobAPIView.as_view(), name='job-list'),
    path('jobs/<int:pk>/', JobAPIView.as_view(), name='job-detail'),

    # JobSkill endpoints
    path('job-skills/', JobSkillAPIView.as_view(), name='jobskill-list'),
    path('job-skills/<int:pk>/', JobSkillAPIView.as_view(), name='jobskill-detail'),
]
