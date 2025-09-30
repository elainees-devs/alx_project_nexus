# jobsboard/request_logs/serializers.py
from rest_framework import serializers
from .models import RequestLog

# ---------------------------------------------------------
# RequestLogSerializer
# ---------------------------------------------------------
# Serializer for the RequestLog model.
# - Converts RequestLog instances to JSON and vice versa.
# - Read-only fields: id and timestamp (cannot be modified via API).
# - Fields include user, IP address, endpoint, HTTP method, status code, and timestamp.

class RequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestLog
        fields = [
            'id',
            'user',
            'ip_address',
            'endpoint',
            'method',
            'status_code',
            'timestamp',
        ]
        read_only_fields = ['id', 'timestamp']
