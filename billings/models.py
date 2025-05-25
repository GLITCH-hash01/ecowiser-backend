from django.db import models
from .subscriptions import SubscriptionTiers,SubscriptionTiers_Details
import uuid
from datetime import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
class Billing(models.Model):
  bill_id= models.UUIDField(primary_key=True, editable=False, auto_created=True,default=uuid.uuid4)
  tenant= models.ForeignKey(
      'tenants.Tenant', on_delete=models.CASCADE, related_name='billing'
  )

  subscription_tier = models.CharField(
      max_length=20, choices=SubscriptionTiers.choices, default=SubscriptionTiers.FREE
  )
  subscription_start_date = models.DateTimeField(default=timezone.now)
  subscription_cancel_date = models.DateTimeField(null=True, blank=True)
  subscription_end_date = models.DateTimeField(null=True, blank=True,default=timezone.now() + relativedelta(months=1))
  price = models.DecimalField(
      max_digits=10, decimal_places=2, default=SubscriptionTiers_Details[SubscriptionTiers.FREE]['price']
  )

  @property
  def is_active(self):
    now = timezone.now()
    """Check if the subscription is active based on the current date and cancellation date."""
    if self.subscription_start_date and self.subscription_start_date > now:
      return False
    if self.subscription_end_date and self.subscription_end_date < now:
      return False
    return True
  


  def __str__(self):
    return f"Billing for {self.tenant.name} - {self.subscription_tier} : {self.subscription_start_date.strftime('%m %Y')}"