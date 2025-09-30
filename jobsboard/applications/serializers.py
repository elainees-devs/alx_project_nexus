from rest_framework import serializers
from .models import Application, ApplicationFile


# ---------------------------------------------------------
# ApplicationFileSerializer
# ---------------------------------------------------------
# Serializes ApplicationFile objects:
# - Validates uploaded files for size and type.
# - Ensures only valid resume, CV, or cover_letter files are accepted.
class ApplicationFileSerializer(serializers.ModelSerializer):
    """
    Serializer for ApplicationFile model.
    Handles validation for file uploads (resume, cv, cover_letter).
    """

    class Meta:
        model = ApplicationFile
        fields = ['id', 'application', 'file_type', 'file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

    def validate_file(self, value):
        """
        Validate uploaded file using model-level rules:
        - File size must be under 5MB
        - File extension must match file_type rules
        """
        # Create a temporary ApplicationFile instance with provided data
        instance = ApplicationFile(file=value, file_type=self.initial_data.get("file_type"))
        # Run model's clean() to trigger validation rules
        instance.clean()
        return value


# ---------------------------------------------------------
# ApplicationSerializer
# ---------------------------------------------------------
# Serializes Application objects:
# - Provides nested files for convenience.
# - Adds applicant/job/reviewer usernames as helper fields.
# - Validates duplicate job applications by the same applicant.
class ApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for Application model.
    Includes nested files and extra read-only fields for convenience.
    """

    # Nested serializer to include related files (read-only, not for creation)
    files = ApplicationFileSerializer(many=True, read_only=True)

    # Extra helper fields for frontend readability
    applicant_username = serializers.CharField(source="applicant.username", read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)
    reviewed_by_username = serializers.CharField(source="reviewed_by.username", read_only=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'job',
            'job_title',
            'applicant',
            'applicant_username',
            'cover_letter',
            'status',
            'applied_at',
            'ip_address',
            'reviewed_by',
            'reviewed_by_username',
            'reviewed_at',
            'files',
        ]
        read_only_fields = ['id', 'applied_at', 'files']

    def validate(self, attrs):
        """
        Ensure applicant can only apply once per job.
        Enforces the unique_together constraint at the serializer level
        to provide user-friendly validation error messages.
        """
        applicant = attrs.get("applicant")
        job = attrs.get("job")

        if applicant and job:
            if Application.objects.filter(job=job, applicant=applicant).exists():
                raise serializers.ValidationError("This applicant has already applied for this job.")
        return attrs
