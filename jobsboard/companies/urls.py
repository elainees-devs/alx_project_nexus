# jobsboard/companies/urls.py
from django.urls import path
from .views import IndustryAPIView, CompanyAPIView

urlpatterns = [
    path("", CompanyAPIView.as_view(), name="company_list"),
    path("<int:pk>/", CompanyAPIView.as_view(), name="company_detail"),
    path("industries/", IndustryAPIView.as_view(), name="industry_list"),
    path("industries/<int:pk>/", IndustryAPIView.as_view(), name="industry_detail"),
]
