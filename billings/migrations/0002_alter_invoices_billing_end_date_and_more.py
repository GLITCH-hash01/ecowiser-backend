# Generated by Django 5.2.1 on 2025-05-31 07:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billings', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoices',
            name='billing_end_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 6, 30, 7, 59, 44, 207196, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='current_cycle_end_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 6, 30, 7, 59, 44, 207196, tzinfo=datetime.timezone.utc)),
        ),
    ]
