#jobsboard/api/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from users.views import home
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

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
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('users.urls')),
    path("api/", include("companies.urls")),
    path("api/", include("jobs.urls")),
    path('api/', include('applications.urls')),
    path('api/', include('payments.urls')),
    path('api/', include('notifications.urls')),
    path('api/', include('rate_limit.urls')),
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    
]

