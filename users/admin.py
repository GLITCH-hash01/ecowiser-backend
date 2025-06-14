from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'tenant')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('role', 'tenant')

admin.site.register(User, UserAdmin)