from django.db import models
import uuid
from django.contrib.auth.hashers import make_password, check_password
from .storage import PublicLogoStorage
from django.utils import timezone
from billings.models import Subscription

# Sets the file name as the tenant's UUID with the original file extension
def tenant_logo_upload_path(instance, filename):
    ext= filename.split('.')[-1]
    return f'{instance.id}.{ext}'

class Tenant(models.Model):

    id = models.UUIDField(primary_key=True, editable=False,auto_created=True,default=uuid.uuid4)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to=tenant_logo_upload_path, blank=True, null=True, storage=PublicLogoStorage())
    contact_email = models.EmailField(max_length=255, unique=True,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  
    

    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        # Set all related users' roles to 'Member'
        self.users.update(role='Member')

        # Delete the logo file if it exists
        if self.logo and self.logo.name:
            self.logo.delete(save=False)
        super().delete(*args, **kwargs)