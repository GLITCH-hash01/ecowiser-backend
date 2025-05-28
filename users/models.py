from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
  """
  This models represents a user in the system.
  Contains the following fields by default:
  - username: The unique username for the user.
  - password: The hashed password for the user.
  - first_name: The first name of the user.
  - last_name: The last name of the user.
  - email: The email address of the user.
  """
  email = models.EmailField(unique=True, blank=False, null=False)
  tenant=models.ForeignKey(
      'tenants.Tenant', on_delete=models.SET_NULL, related_name='users', null=True, blank=True,default=None
  )
  role= models.CharField(
      max_length=20, choices=(
          ('Owner', 'Owner'),
          ('Admin', 'Admin'),
          ('Member', 'Member')
      ), default='Member', blank=False, null=False
  )

  def __str__(self):
    return self.email