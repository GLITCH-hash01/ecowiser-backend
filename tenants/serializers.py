from rest_framework import serializers
from .models import Tenant

class TenantSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    subscription_tier = serializers.CharField(read_only=True)

    class Meta:
        model = Tenant
        fields = ['id', 'name', 'logo', 'subscription_tier', 'subscription_status', 'created_at']
        read_only_fields = ['id', 'created_at']
    
  