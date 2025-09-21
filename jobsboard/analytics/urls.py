#jobsboard/analytics/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobViewAggregateViewSet, JobApplicationAggregateViewSet

router = DefaultRouter()
router.register(r'job-views', JobViewAggregateViewSet, basename='job-views')
router.register(r'job-applications', JobApplicationAggregateViewSet, basename='job-applications')

urlpatterns = [
    path('', include(router.urls)),
]


