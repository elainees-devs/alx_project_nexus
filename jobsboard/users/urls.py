from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthViewSet, SignupViewSet, UsersViewSet,
    UserFileViewSet, ProfileAPIView, users_home
)

# Create router
router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')         # login, logout, password-reset
router.register(r'signup', SignupViewSet, basename='signup')   # public signup
router.register(r'users', UsersViewSet, basename='user')       # Admin-only list
router.register(r'files', UserFileViewSet, basename='userfile') # User files CRUD

# Profile ViewSet
profile_view = ProfileAPIView.as_view({
    'get': 'retrieve_profile',
    'put': 'update_profile'
})

urlpatterns = [
    path("", users_home, name="api-users-home"),

    # Profile endpoint (auth required)
    path("profile/", profile_view, name="api-profile"),

    # Include router endpoints
    path("", include(router.urls)),
]
