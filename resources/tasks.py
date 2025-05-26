import os
import mimetypes
import boto3
from .utils import create_image_thumbnail
from celery import shared_task
from django.conf import settings
from .models import Media,CSVTables
import pandas as pd


@shared_task
def upload_media_and_thumbnail(file_path, file_name, media_id, project_id,visibility):
    """
    Upload original media file and thumbnail (if image) to S3 under
    <project_id>/media/ folder, update Media model with URLs,
    and clean up local thumbnail files.
    """
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
        
    )

    try:
        base_s3_path = f"{project_id}/media"

        with open(file_path, 'rb') as f:
            s3.upload_fileobj(f, settings.AWS_STORAGE_BUCKET_NAME, f'{base_s3_path}/{file_name}',ExtraArgs={'ACL': 'public-read' if visibility == 'Public' else 'private'})

        file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{base_s3_path}/{file_name}"
        thumb_url = None

        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and mime_type.startswith('image/'):

            base_dir, original_filename = os.path.split(file_path)
            thumbnail_dir = os.path.join(base_dir, 'thumbnails')
            os.makedirs(thumbnail_dir, exist_ok=True)
            thumbnail_path = os.path.join(thumbnail_dir, original_filename)


            create_image_thumbnail(file_path, thumbnail_path)

            thumb_s3_path = f"{base_s3_path}/thumbnails/{file_name}"
            with open(thumbnail_path, 'rb') as thumb_file:
                s3.upload_fileobj(thumb_file, settings.AWS_STORAGE_BUCKET_NAME, thumb_s3_path)

            thumb_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{thumb_s3_path}"

            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)

        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else None # bytes
        if os.path.exists(file_path):
            os.remove(file_path)

        media = Media.objects.get(id=media_id)
        media.file=None
        media.file_url = file_url
        media.file_size = file_size
        if thumb_url:
            media.thumb_url = thumb_url
        media.save(update_fields=['file_url', 'thumb_url','file','file_size'])
        return "Media and thumbnail uploaded successfully"

    except Exception as e:
        print(f"Error uploading media and thumbnail: {e}")
        raise


@shared_task
def change_visibilty_file(file_key,visibility):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    try:
      s3.put_object_acl(
          Bucket=settings.AWS_STORAGE_BUCKET_NAME,
          Key=file_key,
          ACL='public-read' if visibility == 'Public' else 'private'
      )
    except Exception as e:
        print(f"Error changing visibility of file {file_key}: {e}")
        raise

@shared_task
def delete_media_file(file_key):
    """Delete a media file from S3."""
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    try:
        s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)
    except Exception as e:
        print(f"Error deleting media file {file_key}: {e}")
        raise
    
@shared_task
def handle_csv(file_path,project_id, csv_id, visibility):
  s3 = boto3.client(
      's3',
      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
      region_name=settings.AWS_S3_REGION_NAME
  )
  try:
    base_s3_path = f"{project_id}/csv"
    with open(file_path, 'rb') as f:
        s3.upload_fileobj(f, settings.AWS_STORAGE_BUCKET_NAME, f'{base_s3_path}/{file_path}')
    print(f"CSV file {file_path} uploaded successfully.")
  except Exception as e:
      print(f"Error uploading CSV file {file_path}: {e}")
      raise
  
  csv={}
  try:
      df = pd.read_csv(file_path)
      csv['columns'] = list(df.columns)
      csv['rows'] = df.to_dict(orient='records')
  except Exception as e:
      print(f"Error reading CSV file {file_path}: {e}")
      raise
  file_size = os.path.getsize(file_path) if os.path.exists(file_path) else None
  if os.path.exists(file_path):
      os.remove(file_path)
  csv_data=CSVTables.objects.get(id=csv_id)
  csv_data.file=None
  csv_data.file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{base_s3_path}/{file_path}"
  csv_data.JSONData= csv
  csv_data.file_size = file_size
  csv_data.save(update_fields=['file_url', 'JSONData','file','file_size'])
  return "CSV file processed successfully"
