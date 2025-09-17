# jobsboard/companies/serializers.py
from rest_framework import serializers
from .models import Industry, Company

class IndustrySerializer(serializers.ModelSerializer):
    """Serializer for Industry model."""
    class Meta:
        model = Industry
        fields = ['id', 'name']
        read_only_fields = ['id']


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
