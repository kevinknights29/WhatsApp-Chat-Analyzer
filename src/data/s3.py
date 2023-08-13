from __future__ import annotations

import os

import boto3
import dotenv

_ = dotenv.load_dotenv(dotenv.find_dotenv())

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.environ.get("AWS_S3_BUCKET")
AWS_S3_LOCATION = os.environ.get("AWS_S3_LOCATION")


__s3_client = None


def s3_client() -> boto3.client:
    global __s3_client
    if __s3_client is None:
        __s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
    return __s3_client


def upload_to_s3(content, filename, bucket_name=AWS_S3_BUCKET) -> str:
    try:
        if isinstance(content, bytes):
            s3_client().put_object(
                Bucket=bucket_name,
                Key=filename,
                Body=content,
                ServerSideEncryption="aws:kms",
            )
        s3_client().upload_fileobj(
            Fileobj=content,
            Bucket=bucket_name,
            Key=filename,
            ServerSideEncryption="aws:kms",
        )
    except Exception as e:
        print("Something Happened: ", e)
        return e
    return filename


def get_data_from_s3(key, bucket_name=AWS_S3_BUCKET) -> str:
    try:
        obj = s3_client().get_object(Bucket=bucket_name, Key=key)
        text = obj["Body"].read().decode("utf-8")
        return text
    except Exception as e:
        print("Something Happened: ", e)
        raise e


def file_exists_in_s3(filename, bucket_name=AWS_S3_BUCKET) -> bool:
    try:
        s3_client().head_object(Bucket=bucket_name, Key=filename)
        return True
    except boto3.exceptions.botocore.client.ClientError:
        return False
