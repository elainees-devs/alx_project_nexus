# jobsboard/notifications/serializers.py
from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'title',
            'message',
            'link',
            'type',
            'is_read',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at']

class NotificationCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "title", "message"]

