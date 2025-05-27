from django.contrib import admin
from .models import Subscription,Invoices
# Register your models here.
admin.site.register(Subscription)
admin.site.register(Invoices)