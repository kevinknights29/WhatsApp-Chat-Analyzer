from __future__ import annotations

import hashlib
import os
import uuid

from werkzeug import utils
from werkzeug.datastructures import FileStorage

from src.utils import config


def allowed_file(filename: str) -> bool:
    condition = (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in config()["ALLOWED_EXTENSIONS"]
    )
    return condition


def hash_filename(file: FileStorage) -> str:
    sha256 = hashlib.sha256()
    file.seek(0)
    while True:
        data = file.read(config()["CHUNK_SIZE"])  # read in 64k chunks
        if not data:
            break
        sha256.update(data)
    file.seek(0)
    return f"{sha256.hexdigest()}.txt"


def unique_filename_generator(filename: str, file: FileStorage) -> str:
    secure_name = utils.secure_filename(filename)
    base, _ = os.path.splitext(secure_name)
    unique_name = f"{base}_{uuid.uuid4()}_{hash_filename(file)}"
    return unique_name
