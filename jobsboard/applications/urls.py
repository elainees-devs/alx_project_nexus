# jobsboard/applications/urls.py
from rest_framework.routers import DefaultRouter
from .views import ApplicationViewSet, ApplicationFileViewSet

router = DefaultRouter()
router.register(r'applications', ApplicationViewSet, basename='application')
router.register(r'applicationfiles', ApplicationFileViewSet, basename='applicationfile')

urlpatterns = router.urls