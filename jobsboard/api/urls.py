from django.contrib import admin
from django.urls import path, include, re_path
from users.views import home
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="JobBoard API",
        default_version="v1",
        description="API documentation for Companies and Industries",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[], # Disable login in Swagger
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),  # root URL
    path('api/users/', include('users.urls')),
    path("api/companies/", include("companies.urls")),
    path("api/jobs/", include("jobs.urls")),
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    
]

