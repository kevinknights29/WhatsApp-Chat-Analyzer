from __future__ import annotations

import duckdb

from src.data import s3


def db_init() -> duckdb.DuckDBPyConnection:
    db = duckdb.connect(":memory:")
    duckdb.install_extension(connection=db, extension="httpfs")
    duckdb.load_extension(connection=db, extension="httpfs")
    db.execute(f"SET s3_region='{s3.AWS_S3_REGION}'")
    db.execute(f"SET s3_access_key_id='{s3.AWS_ACCESS_KEY_ID}'")
    db.execute(f"SET s3_secret_access_key='{s3.AWS_SECRET_ACCESS_KEY}'")
    return db
