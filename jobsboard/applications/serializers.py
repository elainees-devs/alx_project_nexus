# jobsboard/applications/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import Application, ApplicationFile
from jobs.models import Job
from users.models import User


# ----------------------------
# ApplicationFile Serializer
# ----------------------------
class ApplicationFileSerializer(serializers.ModelSerializer):
    """Serializer for ApplicationFile model."""

    class Meta:
        model = ApplicationFile
        fields = ["id", "file_type", "file_path", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]


# ----------------------------
# Application Serializer
# ----------------------------
class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer for Application model."""

    applicant = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all())
    files = ApplicationFileSerializer(many=True, read_only=True)
    reviewed_by = serializers.StringRelatedField(read_only=True)  # show username
    reviewed_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "job",
            "applicant",
            "cover_letter",
            "status",
            "applied_at",
            "ip_address",
            "files",
            "reviewed_by",
            "reviewed_at",
        ]
        read_only_fields = ["id", "applied_at", "ip_address", "reviewed_by", "reviewed_at"]

    def validate_status(self, value):
        """Validate that status is one of the allowed choices."""
        valid_choices = [choice[0] for choice in Application.APPLICATION_STATUS_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(f"Status must be one of {valid_choices}.")
        return value

    def update(self, instance, validated_data):
        """
        If status is changed to 'reviewd', set reviewed_by and reviewed_at automatically.
        """
        request = self.context.get("request")
        new_status = validated_data.get("status", instance.status)

        if instance.status != "reviewd" and new_status == "reviewd":
            if request and request.user.is_authenticated:
                instance.reviewed_by = request.user
            instance.reviewed_at = timezone.now()

        return super().update(instance, validated_data)
