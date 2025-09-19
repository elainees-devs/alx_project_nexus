# jobsboard/request_logs/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RequestLogViewSet

router = DefaultRouter()
router.register(r'request-logs', RequestLogViewSet, basename="request-logs")

urlpatterns = [
    path("", include(router.urls)),
]
