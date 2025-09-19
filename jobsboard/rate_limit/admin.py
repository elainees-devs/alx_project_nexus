# jobsboard/rate_limit/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import RateLimitAction, RateLimit


@admin.register(RateLimitAction)
class RateLimitActionAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(RateLimit)
class RateLimitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "action",
        "count",
        "period_start",
        "period_seconds",
    )
    list_filter = ("action", "period_seconds")
    search_fields = ("user__username", "action__name")
    ordering = ("-period_start",)

    # -------------------------
    # Custom admin action
    # -------------------------
    actions = ["reset_counts"]

    def reset_counts(self, request, queryset):
        updated = queryset.update(count=0)
        self.message_user(
            request,
            _(f"Successfully reset count for {updated} rate limit(s)."),
        )

    reset_counts.short_description = _("Reset selected rate limit counters")
