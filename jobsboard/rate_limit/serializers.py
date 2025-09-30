#jobsboard/rate_limit/serializers.py
from rest_framework import serializers

# ---------------------------------------------------------
# RateLimitStatusSerializer
# ---------------------------------------------------------
# Serializer for returning a user's current rate limit status.
# - Fields:
#    - limit: maximum allowed requests for the action within the period.
#    - remaining: remaining requests available for the user.
#    - reset: time in seconds until the rate limit period resets.

class RateLimitStatusSerializer(serializers.Serializer):
    limit = serializers.IntegerField()
    remaining = serializers.IntegerField()
    reset = serializers.IntegerField()

# ---------------------------------------------------------
# ThrottledResponseSerializer
# ---------------------------------------------------------
# Serializer for returning a response when a user exceeds a rate limit.
# - Fields:
#    - detail: message describing the rate limit violation.
#    - wait: time in seconds the user must wait before retrying.
class ThrottledResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    wait = serializers.IntegerField()

