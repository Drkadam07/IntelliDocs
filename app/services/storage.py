# app/services/storage.py
import logging
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from app.config import settings

logger = logging.getLogger(__name__)

def get_neon_s3_client():
    return boto3.client(
        service_name="s3",
        endpoint_url=settings.NEON_STORAGE_ENDPOINT,
        aws_access_key_id=settings.NEON_STORAGE_ACCESS_KEY_ID,
        aws_secret_access_key=settings.NEON_STORAGE_SECRET_ACCESS_KEY,
        region_name=settings.NEON_STORAGE_REGION,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"}  # Required for Neon Object Storage
        )
    )

def ensure_bucket_exists(s3_client=None):
    """Verifies the bucket exists; if not, creates it automatically."""
    client = s3_client or get_neon_s3_client()
    bucket = settings.NEON_STORAGE_BUCKET_NAME

    try:
        client.head_bucket(Bucket=bucket)
    except ClientError as e:
        error_code = str(e.response.get("Error", {}).get("Code", ""))
        # 404 or NoSuchBucket means the bucket needs provisioning
        if error_code in ["404", "NoSuchBucket", "NotFound"]:
            logger.info(f"Bucket '{bucket}' not found. Creating it now...")
            try:
                # In standard S3 compatible endpoints outside us-east-1,
                # LocationConstraint may be omitted or required depending on the region.
                if settings.NEON_STORAGE_REGION and settings.NEON_STORAGE_REGION != "us-east-1":
                    client.create_bucket(
                        Bucket=bucket,
                        CreateBucketConfiguration={"LocationConstraint": settings.NEON_STORAGE_REGION}
                    )
                else:
                    client.create_bucket(Bucket=bucket)
                logger.info(f"Successfully created bucket: {bucket}")
            except ClientError as create_err:
                # If LocationConstraint failed, fallback to unadorned create_bucket
                client.create_bucket(Bucket=bucket)
        else:
            raise e

def upload_file_to_neon(file_bytes: bytes, key: str, content_type: str = "application/pdf") -> str:
    """Uploads document bytes to Neon Object Storage bucket, auto-creating the bucket if needed."""
    s3_client = get_neon_s3_client()
    bucket = settings.NEON_STORAGE_BUCKET_NAME

    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=file_bytes,
            ContentType=content_type
        )
    except ClientError as err:
        error_code = str(err.response.get("Error", {}).get("Code", ""))
        if error_code in ["NoSuchBucket", "404"]:
            ensure_bucket_exists(s3_client)
            # Retry upload after provisioning
            s3_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=file_bytes,
                ContentType=content_type
            )
        else:
            raise err

    return key

def get_file_from_neon(key: str) -> bytes:
    """Retrieves document bytes from Neon Object Storage."""
    s3_client = get_neon_s3_client()
    response = s3_client.get_object(
        Bucket=settings.NEON_STORAGE_BUCKET_NAME,
        Key=key
    )
    return response["Body"].read()

def delete_file_from_neon(key: str):
    """Deletes an object from Neon Object Storage."""
    s3_client = get_neon_s3_client()
    try:
        s3_client.delete_object(
            Bucket=settings.NEON_STORAGE_BUCKET_NAME,
            Key=key
        )
    except ClientError:
        pass

def generate_neon_download_url(key: str, expires_in: int = 3600) -> str:
    """Generates a temporary presigned download URL."""
    s3_client = get_neon_s3_client()
    return s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.NEON_STORAGE_BUCKET_NAME,
            "Key": key
        },
        ExpiresIn=expires_in
    )