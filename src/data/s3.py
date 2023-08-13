from __future__ import annotations

import os

import boto3
import dotenv

_ = dotenv.load_dotenv(dotenv.find_dotenv())

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.environ.get("AWS_S3_BUCKET")
AWS_S3_LOCATION = os.environ.get("AWS_S3_LOCATION")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


def upload_to_s3(file, filename, bucket_name=AWS_S3_BUCKET) -> str:
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=file,
            ContentType=file.content_type,
            ServerSideEncryption="aws:kms",
        )
    except Exception as e:
        print("Something Happened: ", e)
        return e
    return filename
