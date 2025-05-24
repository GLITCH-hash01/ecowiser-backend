from storages.backends.s3boto3 import S3Boto3Storage

class PublicLogoStorage(S3Boto3Storage):
    location = 'tenant_logos'
    default_acl = 'public-read'
    file_overwrite = False