from __future__ import annotations

import re

import duckdb
import pandas as pd
import polars as pl

from src.data import db
from src.data import s3


def extract(txt_file_path: str) -> pl.DataFrame:
    pattern = r"\[(.*?)\] (.*?): (.*)"
    with open(txt_file_path) as file:
        text = file.read()
    matches = re.findall(pattern, text)
    columns = ["Date", "Sender", "Message"]
    df = pd.DataFrame(matches, columns=columns)
    return pl.DataFrame(df)


def extract_from_s3(key: str, bucket: str = s3.AWS_S3_BUCKET) -> pl.DataFrame:
    data = s3.get_data_from_s3(key, bucket_name=bucket)
    if not data:
        raise ValueError(f"Failed to fetch data for key: {key} from bucket: {bucket}")
    pattern = r"\[(.*?)\] (.*?): (.*)"
    matches = re.findall(pattern, data)
    columns = ["Date", "Sender", "Message"]
    df = pd.DataFrame(matches, columns=columns)
    return pl.DataFrame(df)


def transform(df: pl.DataFrame, output_file_path: str) -> str:
    df.write_parquet(output_file_path)
    return output_file_path


def transform_to_s3(df: pl.DataFrame, key: str, bucket: str = s3.AWS_S3_BUCKET) -> str:
    parquet_bytes = df.to_pandas().to_parquet(index=False)
    try:
        return s3.upload_to_s3(parquet_bytes, key, bucket_name=bucket)
    except Exception as e:
        print("Something Happened: ", e)
        raise e


def load(output_file_path: str) -> duckdb.DuckDBPyConnection:
    db = duckdb.connect(":memory:")
    create_view_query = f"""
        --sql
        CREATE VIEW chat_history AS
        SELECT *
        FROM parquet_scan('{output_file_path}');
    """
    db.execute(create_view_query)
    return db


def load_from_s3(key: str, bucket: str = s3.AWS_S3_BUCKET) -> duckdb.DuckDBPyConnection:
    db_conn = db.db_init()
    parquet_s3_path = f"s3://{bucket}/{key}"
    create_view_query = f"""
        --sql
        CREATE VIEW chat_history AS
        SELECT *
        FROM parquet_scan('{parquet_s3_path}');
    """
    duckdb.query(connection=db_conn, query=create_view_query)
    return db_conn


def etl_pipeline(key: str, bucket=s3.AWS_S3_BUCKET) -> duckdb.DuckDBPyConnection:
    parquet_key = key.replace(".txt", ".parquet")
    if not s3.file_exists_in_s3(parquet_key, bucket_name=bucket):
        df = extract_from_s3(key, bucket)
        transform_to_s3(df, parquet_key, bucket)
    db_conn = load_from_s3(parquet_key, bucket)
    return db_conn
