from django.db import models
import uuid
from billings.subscriptions import SubscriptionTiers
from django.contrib.auth.hashers import make_password, check_password
from .storage import PublicLogoStorage
from django.utils import timezone
from billings.models import Billing

# Sets the file name as the tenant's UUID with the original file extension
def tenant_logo_upload_path(instance, filename):
    ext= filename.split('.')[-1]
    return f'{instance.id}.{ext}'

class Tenant(models.Model):

    id = models.UUIDField(primary_key=True, editable=False,auto_created=True,default=uuid.uuid4)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to=tenant_logo_upload_path, blank=True, null=True, storage=PublicLogoStorage())
    subscription_status= models.CharField(
        max_length=20, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active'
    )
    # subscription_tier=models.CharField(max_length=20, choices=SubscriptionTiers.choices, default=SubscriptionTiers.FREE)
    created_at = models.DateTimeField(auto_now_add=True)  
    
    @property
    def subscription_tier(self):
        now=timezone.now()
        tier=Billing.objects.filter(tenant=self, 
                                    subscription_start_date__lte=now,
                                    subscription_cancel_date__isnull=True).first()
        if tier:
            return tier.subscription_tier
    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        # Set all related users' roles to 'Member'
        self.users.update(role='Member')

        # Delete the logo file if it exists
        if self.logo and self.logo.name:
            self.logo.delete(save=False)
        super().delete(*args, **kwargs)