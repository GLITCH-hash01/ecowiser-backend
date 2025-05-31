from django.db import models
import uuid
from storages.backends.s3boto3 import S3Boto3Storage

# Custom storage class for public logo storage on S3
class PublicLogoStorage(S3Boto3Storage):
    location = 'tenant_logos'
    default_acl = 'public-read'
    file_overwrite = False

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
    
    def update(self, *args, **kwargs):
        # Delete the old logo file if a new one is being uploaded
        if 'logo' in kwargs and self.logo:
            self.logo.delete(save=False)
        super().update(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.pk:
            old = Tenant.objects.filter(pk=self.pk).first()
            if old and old.logo and self.logo and old.logo.name != self.logo.name:
                old.logo.delete(save=False)
        super().save(*args, **kwargs)