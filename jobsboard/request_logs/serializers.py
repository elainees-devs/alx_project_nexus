# jobsboard/request_logs/serializers.py
from rest_framework import serializers
from .models import RequestLog

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
