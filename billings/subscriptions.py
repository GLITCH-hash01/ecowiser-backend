from django.db import models

SubscriptionTiers_Details={
  'Free': {
    'projects':2,
    'price': 0.0,
  },
  'Pro': {
  'price': 9.99,  # Monthly price in USD
    'projects':5,
  },
  'Enterprise': {
    'price': 49.99,  # Monthly price in USD
    'projects': None,  # Unlimited projects
  }
}

class SubscriptionTiers(models.TextChoices):
  FREE= 'Free', 'Free'
  PRO= 'Pro', 'Pro'
  ENTERPRISE= 'Enterprise', 'Enterprise'