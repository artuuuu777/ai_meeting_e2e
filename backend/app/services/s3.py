from typing import Optional

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class S3Service:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            endpoint_url=settings.AWS_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4"),
        )

    def generate_presigned_upload_url(
        self,
        bucket: str,
        key: str,
        content_type: str = "application/octet-stream",
        expires_in: int = 3600,
    ) -> str:
        """Generate a presigned URL for uploading a file to S3."""
        try:
            url = self.client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": bucket,
                    "Key": key,
                    "ContentType": content_type,
                },
                ExpiresIn=expires_in,
            )
            return url
        except ClientError as e:
            logger.error("Failed to generate presigned URL", error=str(e))
            raise

    def generate_presigned_download_url(
        self, bucket: str, key: str, expires_in: int = 3600
    ) -> str:
        """Generate a presigned URL for downloading a file from S3."""
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expires_in,
            )
            return url
        except ClientError as e:
            logger.error("Failed to generate presigned URL", error=str(e))
            raise

    def upload_file(
        self,
        bucket: str,
        key: str,
        file_content: bytes,
        content_type: Optional[str] = None,
    ) -> None:
        """Upload a file to S3."""
        try:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type

            self.client.put_object(
                Bucket=bucket, Key=key, Body=file_content, **extra_args
            )
            logger.info("File uploaded to S3", bucket=bucket, key=key)
        except ClientError as e:
            logger.error("Failed to upload file to S3", error=str(e))
            raise

    def download_file(self, bucket: str, key: str) -> bytes:
        """Download a file from S3."""
        try:
            response = self.client.get_object(Bucket=bucket, Key=key)
            return response["Body"].read()
        except ClientError as e:
            logger.error("Failed to download file from S3", error=str(e))
            raise

    def delete_file(self, bucket: str, key: str) -> None:
        """Delete a file from S3."""
        try:
            self.client.delete_object(Bucket=bucket, Key=key)
            logger.info("File deleted from S3", bucket=bucket, key=key)
        except ClientError as e:
            logger.error("Failed to delete file from S3", error=str(e))
            raise

    def list_files(self, bucket: str, prefix: str = "") -> list:
        """List files in S3 bucket with optional prefix."""
        try:
            response = self.client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            if "Contents" not in response:
                return []
            return [obj["Key"] for obj in response["Contents"]]
        except ClientError as e:
            logger.error("Failed to list files in S3", error=str(e))
            raise