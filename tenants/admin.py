from django.contrib import admin
from .models import Tenant

class TenantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'logo', 'contact_email', 'created_at')
    search_fields = ('name', 'contact_email')
    readonly_fields = ('created_at',)

admin.site.register(Tenant, TenantAdmin)