from django.db import models

class Media(models.Model):
    """
    This model represents a media file in the system.
    Contains the following fields:
    - file: The media file itself.
    - name: The name of the media file.
    - description: A description of the media file.
    - created_at: The date and time when the media file was created.
    - updated_at: The date and time when the media file was last updated.
    """
    project= models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE, related_name='media', blank=False
    )
    file = models.FileField(upload_to='media/projects/media/')
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file_url = models.URLField(blank=True, null=True)
    thumb_url = models.URLField(blank=True, null=True)
    visibility = models.CharField(
        max_length=20, choices=[('Public', 'Public'), ('Private', 'Private')], default='Private'
    )
    uploaded_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, related_name='media', null=True
    )
    file_size = models.BigIntegerField(blank=True, null=True)
    def __str__(self):
        return self.name

class CSVTables(models.Model):
    """
    This model represents a CSV file in the system.
    Contains the following fields:
    - file: The CSV file itself.
    - name: The name of the CSV file.
    - description: A description of the CSV file.
    - created_at: The date and time when the CSV file was created.
    - updated_at: The date and time when the CSV file was last updated.
    """
    project= models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE, related_name='csv_tables', blank=False
    )
    file = models.FileField(upload_to='media/projects/csv/')
    file_url = models.URLField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    JSONData = models.JSONField(blank=True, null=True)
    uploaded_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, related_name='csv_tables', null=True
    )
    file_size = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # Delete the file from storage
        if self.file:
            self.file.delete(save=False)
        super().delete(*args, **kwargs)
