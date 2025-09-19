from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer, NotificationCreateSerializer
from drf_yasg.utils import swagger_auto_schema

# -----------------------------
# Notification ViewSet
# -----------------------------
class NotificationViewSet(viewsets.ModelViewSet):
     """
    API endpoint for managing notifications.
    """
     queryset=Notification.objects.all()

     # Public GET, others require authentication
     def get_permissions(self):
          if self.action in ['list', 'retrieve']:
               return [permissions.IsAuthenticated()]
          return [permissions.IsAuthenticated()]
     
     def get_serializer_class(self):
          if self.action in ['create']:
               return NotificationCreateSerializer
          return NotificationSerializer
     
     def perform_create(self, serializer):
          serializer.save(user=self.request.user)
     
     @swagger_auto_schema(security=[{"Bearer":[]}])
     def list(self, request, *args,**kwargs):
          self.queryset=Notification.objects.filter(user=request.user).order_by('created_at')
          return super().list(request, *args, **kwargs)
     
     @swagger_auto_schema(security=[{"Bearer":[]}])
     def retrieve(self, request, *args,**kwargs):
          return super().retrieve(request, *args, **kwargs)
     
     @swagger_auto_schema(security=[{"Bearer":[]}])
     def create(self, request, *args,**kwargs):
          return super().create(request, *args, **kwargs)
     
     @swagger_auto_schema(security=[{"Bearer":[]}])
     def update(self, request, *args,**kwargs):
          return super().update(request, *args, **kwargs)

     @swagger_auto_schema(security=[{"Bearer":[]}])
     def partial_update(self, request, *args,**kwargs):
          return super().partial_update(request, *args, **kwargs)
     
     @swagger_auto_schema(security=[{"Bearer":[]}])
     def destroy(self, request, *args,**kwargs):
          return super().destroy(request, *args, **kwargs)
     
     # -----------------------------
    # Custom action to mark notification as read
    # -----------------------------
     @swagger_auto_schema(security=[{"Bearer": []}])
     @action(detail=True, methods=['post'])
     def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "read"}, status=status.HTTP_200_OK)