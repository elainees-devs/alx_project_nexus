# jobsboard/rate_limit/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RateLimitViewSet

router = DefaultRouter()
router.register(r'rate-limit', RateLimitViewSet, basename="rate-limit")

urlpatterns = [
    path("", include(router.urls)),
]
