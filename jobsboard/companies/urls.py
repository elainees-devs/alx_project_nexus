# jobsboard/companies/urls.py
from django.urls import path
from .views import IndustryAPIView, CompanyAPIVIEW

urlpatterns = [
    path("industries/", IndustryAPIView.as_view(), name="industry_list"),
    path("industries/<int:pk>/", IndustryAPIView.as_view(), name="industry_detail"),
    path("companies/", CompanyAPIVIEW.as_view(), name="company_list"),
    path("companies/<int:pk>/", CompanyAPIVIEW.as_view(), name="company_detail"),
]