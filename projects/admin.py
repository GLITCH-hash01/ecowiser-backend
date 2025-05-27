from django.contrib import admin
from .models import Project 

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'tenant', 'created_at', 'updated_at')
    list_filter = ('tenant', )
    search_fields = ('name', 'tenant__name')
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(Project, ProjectAdmin)