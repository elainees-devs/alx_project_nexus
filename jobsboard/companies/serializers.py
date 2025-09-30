from rest_framework import serializers
from .models import Industry, Company


# ---------------------------------------------------------
# IndustrySerializer
# ---------------------------------------------------------
# Serializes Industry model data.
# - Provides ID and name fields.
# - ID is read-only to prevent modification.
class IndustrySerializer(serializers.ModelSerializer):
    """Serializer for Industry model."""

    class Meta:
        model = Industry
        fields = ['id', 'name']
        read_only_fields = ['id']


# ---------------------------------------------------------
# CompanySerializer
# ---------------------------------------------------------
# Serializes Company model data.
# - Includes company details such as name, description, industry, and owner.
# - Owner is automatically set to the logged-in user during creation.
# - ID, owner, and timestamps are read-only fields.
class CompanySerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")  # owner is read-only

    class Meta:
        model = Company
        fields = ["id", "name", "description", "industry", "owner", "created_at", "updated_at"]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def create(self, validated_data):
        # Automatically assign the logged-in user as the owner, if available
        request = self.context.get("request", None)
        if request and hasattr(request, "user"):
            validated_data["owner"] = request.user
        return super().create(validated_data)
