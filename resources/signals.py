from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Media,CSVTables
from .tasks import upload_media_and_thumbnail,handle_csv

@receiver(post_save, sender=Media)
def upload_media_after_save(sender, instance, created, **kwargs):
    if created and instance.file:
        project_id = instance.project.id 
        file_path = instance.file.path
        file_name = instance.file.name.split('/')[-1]
        visibility = instance.visibility
        upload_media_and_thumbnail.delay(file_path, file_name, str(instance.id), project_id, visibility)  

@receiver(post_save, sender=CSVTables)
def upload_csv_after_save(sender, instance, created, **kwargs):
    if created and instance.file:
        project_id = instance.project.id 
        file_path = instance.file.path
        file_name = instance.file.name.split('/')[-1]
        handle_csv.delay(file_path, project_id, str(instance.id),file_name)