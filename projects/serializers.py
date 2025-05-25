from rest_framework.serializers import ModelSerializer
from .models import Project

class ProjectSerializer(ModelSerializer):
  class Meta:
    model = Project
    fields = ['id', 'name', 'description', 'tenant','created_by', 'created_at', 'updated_at']
    read_only_fields = ['id', 'created_at']
