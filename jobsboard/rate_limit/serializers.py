#jobsboard/rate_limit/serializers.py
from rest_framework import serializers

class RateLimitStatusSerializer(serializers.Serializer):
    limit = serializers.IntegerField()
    remaining = serializers.IntegerField()
    reset = serializers.IntegerField()

class ThrottledResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    wait = serializers.IntegerField()

