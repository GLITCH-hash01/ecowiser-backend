from rest_framework.serializers import ModelSerializer,BooleanField,DateTimeField
from .models import Billing

class BillingsSerializer(ModelSerializer):
  is_active=BooleanField(read_only=True)
  class Meta:
    model = Billing
    fields=['bill_id','tenant','subscription_tier','subscription_start_date','subscription_cancel_date','price','is_active','subscription_end_date']