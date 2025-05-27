from django.contrib import admin
from .models import Subscription,Invoices

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'subscription_tier', 'current_cycle_start_date', 'current_cycle_end_date', 'auto_renew')
    search_fields = ('tenant__name', 'subscription_tier')
    readonly_fields = ('created_at',)
class InvoicesAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'tenant', 'subscription_id', 'amount', 'issued_at')
    search_fields = ('tenant__name', 'subscription_id__subscription_tier', 'invoice_id')
    list_filter = ('tenant', 'subscription_id__subscription_tier')
    readonly_fields = ('issued_at',)

admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Invoices, InvoicesAdmin)