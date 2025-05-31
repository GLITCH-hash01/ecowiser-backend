from django.db import models
import uuid

class Project(models.Model):
    id = models.UUIDField(primary_key=True, editable=False,auto_created=True,default=uuid.uuid4)
    name = models.CharField(max_length=255)
    description = models.TextField()
    tenant= models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE, related_name='projects', blank=False
    )
    created_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, related_name='projects', null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name