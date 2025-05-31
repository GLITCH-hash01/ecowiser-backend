from rest_framework.serializers import ModelSerializer
from .models import Subscription,Invoices


class SubscriptionSerializer(ModelSerializer):
  class Meta:
    model = Subscription
    fields = '__all__'
    read_only_fields = ['created_at']

class InvoicesSerializer(ModelSerializer):
  class Meta:
    model = Invoices
    fields = '__all__'
    read_only_fields = ['issued_at']
