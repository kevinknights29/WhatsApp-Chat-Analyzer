from __future__ import annotations

import hashlib
import os

from werkzeug import utils
from werkzeug.datastructures import FileStorage

from src.utils import config


def allowed_file(filename: str) -> bool:
    condition = (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in config.config()["ALLOWED_EXTENSIONS"]
    )
    return condition


def compute_hash(file: FileStorage) -> str:
    sha256 = hashlib.sha256()
    file.seek(0)
    while True:
        data = file.read(config.config()["CHUNK_SIZE"])  # read in 64k chunks
        if not data:
            break
        sha256.update(data)
    file.seek(0)
    return sha256.hexdigest()


def unique_filename_generator(
    filename: str,
    file: FileStorage,
    sha256_hash: str = None,
) -> str:
    secure_name = utils.secure_filename(filename)
    base, ext = os.path.splitext(secure_name)
    if sha256_hash is None:
        sha256_hash = compute_hash(file)
    unique_name = f"{base}_{sha256_hash}.{ext}"
    return unique_name
