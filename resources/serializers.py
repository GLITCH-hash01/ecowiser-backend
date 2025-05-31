from rest_framework.serializers import ModelSerializer,SerializerMethodField,FileField
from .models import Media,CSVTables
from .utils import create_signed_url
import ecowiser.settings as settings

class MediaSerializer(ModelSerializer):
    file_url = SerializerMethodField()
    thumb_url = SerializerMethodField()
    file=FileField(write_only=True)
    class Meta:
        model = Media
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'file_url', 'thumb_url']

    # These methods retrieve the file URL based on the visibility of the media instance.
    # Creates a signed URL for private files if visibility is set to 'Private'.
    def get_file_url(self,instance):
        if not instance.file_url:
            return None
        if instance.visibility == 'Public':
            return instance.file_url
        else:
            print("Retrieving signed URL for private file")
            file_url=instance.file_url.removeprefix(f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/')
            return create_signed_url(file_url, expiration=3600)

    def get_thumb_url(self,instance):
        if not instance.thumb_url:
            return None
        if instance.visibility == 'Public':
            return instance.thumb_url
        else:
            thumb_url=instance.thumb_url.removeprefix(f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/')
            return create_signed_url(thumb_url, expiration=3600)
        
class CSVTablesSerializer(ModelSerializer):
    file_url = SerializerMethodField()
    file=FileField(write_only=True)

    class Meta:
        model = CSVTables
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'file_url']

    def get_file_url(self, instance):
        if not instance.file_url:
            return None
        file_url = instance.file_url.removeprefix(f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/')
        return create_signed_url(file_url, expiration=3600)
    
