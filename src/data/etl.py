from __future__ import annotations

import re

import duckdb
import pandas as pd
import polars as pl

from src.data import s3


def extract(txt_file_path: str) -> pl.DataFrame:
    pattern = r"\[(.*?)\] (.*?): (.*)"
    with open(txt_file_path) as file:
        text = file.read()
    matches = re.findall(pattern, text)
    columns = ["Date", "Sender", "Message"]
    df = pd.DataFrame(matches, columns=columns)
    return pl.DataFrame(df)


def extract_from_s3(key: str, bucket=s3.AWS_S3_BUCKET) -> pl.DataFrame:
    data = s3.get_data_from_s3(key, bucket_name=bucket)
    if not data:
        print(f"Failed to fetch data for key: {key} from bucket: {bucket}")
        return pl.DataFrame()
    pattern = r"\[(.*?)\] (.*?): (.*)"
    matches = re.findall(pattern, data)
    columns = ["Date", "Sender", "Message"]
    df = pd.DataFrame(matches, columns=columns)
    return pl.DataFrame(df)


def transform(df: pl.DataFrame, output_file_path: str) -> str:
    df.write_parquet(output_file_path)
    return output_file_path


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


def etl_pipeline(key: str, bucket=s3.AWS_S3_BUCKET) -> duckdb.DuckDBPyConnection:
    df = extract_from_s3(key, bucket)
    output_file_path = key.replace(".txt", ".parquet")
    output_file_path = transform(df, output_file_path)
    db = load(output_file_path)
    return db
