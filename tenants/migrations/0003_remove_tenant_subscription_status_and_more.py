# Generated by Django 5.2.1 on 2025-05-27 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0002_remove_tenant_subscription_tier_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tenant',
            name='subscription_status',
        ),
        migrations.AddField(
            model_name='tenant',
            name='contact_email',
            field=models.EmailField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]
