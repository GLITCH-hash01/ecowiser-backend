from django.contrib import admin
from .models import Media, CSVTables

class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'file', 'visibility', 'created_at')
    search_fields = ('project__name', 'file')
    list_filter = ('visibility', 'created_at')
    readonly_fields = ('created_at',)

class CSVTablesAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'file', 'created_at')
    search_fields = ('project__name', 'file')
    readonly_fields = ('created_at',)

admin.site.register(Media, MediaAdmin)
admin.site.register(CSVTables, CSVTablesAdmin)