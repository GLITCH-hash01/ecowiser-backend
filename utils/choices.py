from django.db import models

class SubscriptionTiers(models.TextChoices):
  FREE= 'Free', 'Free'
  PRO= 'Pro', 'Pro'
  ENTERPRISE= 'Enterprise', 'Enterprise'
