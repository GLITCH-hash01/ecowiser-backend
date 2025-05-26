import boto3
import ecowiser.settings as settings
from PIL import Image


def create_image_thumbnail(input_path, output_path, size=(200, 200)):
    """Create a thumbnail for an image file."""
    with Image.open(input_path) as img:
        img.thumbnail(size)
        img.save(output_path)

def create_signed_url( object_key, expiration=3600):

    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    try:
        signed_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': object_key},
            ExpiresIn=expiration
        )
        return signed_url
    except Exception as e:
        print(f"Error generating signed URL: {e}")
        return None