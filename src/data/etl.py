from __future__ import annotations

import duckdb
import polars as pl


def extract(txt_file_path: str) -> pl.DataFrame:
    df = pl.read_csv(
        txt_file_path,
        separator="\t",
        has_header=False,
        use_pyarrow=True,
        ignore_errors=True,
    )
    return df


def transform(df: pl.DataFrame, output_file_path: str) -> str:
    df.write_parquet(output_file_path)
    return output_file_path


def load(output_file_path: str) -> duckdb.DuckDBPyConnection:
    db = duckdb.connect(":memory:")
    create_view_query = """
        --sql
        CREATE VIEW chat_history AS
        SELECT *
        FROM parquet_scan(?);
    """
    db.execute(create_view_query, (output_file_path,))
    return db


def etl_pipeline(txt_file_path: str) -> duckdb.DuckDBPyConnection:
    df = extract(txt_file_path)
    output_file_path = txt_file_path.replace(".txt", ".parquet")
    output_file_path = transform(df, output_file_path)
    db = load(output_file_path)
    return db
