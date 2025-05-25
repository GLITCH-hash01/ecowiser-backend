from django.db import models

SubscriptionTiers_Limits={
  'Free': {
    'projects':2,
  },
  'Pro': {
    'projects':5,
  },
  'Enterprise': {
    'projects': None,  # Unlimited projects
  }
}

class SubscriptionTiers(models.TextChoices):
  FREE= 'Free', 'Free'
  PRO= 'Pro', 'Pro'
  ENTERPRISE= 'Enterprise', 'Enterprise'
