# jobsboard/request_logs/admin.py
from django.contrib import admin
from .models import RequestLog

@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "ip_address", "endpoint", "method", "status_code", "timestamp")
    list_filter = ("method", "status_code", "timestamp")
    search_fields = ("user__username", "ip_address", "endpoint")
    ordering = ("-timestamp",)
