from rest_framework import serializers
from .models import Industry, Company

class IndustrySerializer:
    """Serializer for Industry model."""
   

    class Meta:
        model = Industry
        fields = ['id', 'name']
        read_only_fields = ['id']


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model."""
    industry = IndustrySerializer(read_only=True)
    owner = serializers.StringRelatedField()  # Display owner's username

    class Meta:
        model = Company
        fields = ['id', 'name', 'description', 'logo', 'website', 'industry', 'owner', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']