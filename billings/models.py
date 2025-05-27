from django.db import models
import uuid
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from ecowiser.settings import SUBSCRIPTION_TIERS_DETAILS


class Subscription(models.Model):
  tenant= models.OneToOneField(
      'tenants.Tenant', on_delete=models.CASCADE, related_name='subscriptions', blank=False
  )
  subscription_tier = models.CharField(
      max_length=20, choices=[(tier, tier) for tier in SUBSCRIPTION_TIERS_DETAILS.keys()], default='Free'
  )
  current_cycle_start_date = models.DateTimeField(default=timezone.now)
  current_cycle_end_date = models.DateTimeField(default=timezone.now() + relativedelta(months=1))
  next_subscription_tier= models.CharField(
      max_length=20, choices=[(tier, tier) for tier in SUBSCRIPTION_TIERS_DETAILS.keys()], default='Free'
  )
  auto_renew = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return f"{self.tenant.name} - {self.subscription_tier} Subscription"
  

class Invoices(models.Model):
  invoice_id = models.UUIDField(primary_key=True, editable=False, auto_created=True, default=uuid.uuid4)
  tenant = models.ForeignKey(
      'tenants.Tenant', on_delete=models.CASCADE, related_name='invoices', blank=False
  )
  subscription_id= models.ForeignKey(
      Subscription, on_delete=models.CASCADE, related_name='invoices', blank=False
  )
  amount = models.DecimalField(max_digits=10, decimal_places=2)
  billing_start_date = models.DateTimeField(default=timezone.now)
  billing_end_date = models.DateTimeField(default=timezone.now() + relativedelta(months=1))
  issued_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return f"Invoice {self.invoice_id} for {self.tenant.name} - {self.subscription_id.subscription_tier}"