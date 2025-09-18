# jobsboard/companies/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IndustryViewSet, CompanyViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'industries', IndustryViewSet, basename='industry')

urlpatterns = [
    path("", include(router.urls)),
]
