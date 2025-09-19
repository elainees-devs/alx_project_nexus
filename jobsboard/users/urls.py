#jobsboard/users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UsersViewSet, UserFileViewSet, SignUpAPIView, ProfileAPIView, users_home

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')        # login, logout, password-reset, set-new-password
router.register(r'users', UsersViewSet, basename='user')      # Admin-only list
router.register(r'files', UserFileViewSet, basename='userfile') # User files CRUD

# For ViewSets with custom actions, define the mapping to HTTP methods
signup_view = SignUpAPIView.as_view({'post': 'signup'})
profile_view = ProfileAPIView.as_view({
    'get': 'retrieve_profile',
    'put': 'update_profile'
})

urlpatterns = [
    path("", users_home, name="api-users-home"),

    # Signup and profile endpoints
    path("signup/", signup_view, name="api-signup"),
    path("profile/", profile_view, name="api-profile"),

    # Include router endpoints
    path("", include(router.urls)),
]
