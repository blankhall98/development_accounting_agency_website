from __future__ import annotations

import os
import uuid
from functools import lru_cache
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from app.config import settings

try:
    import firebase_admin
    from firebase_admin import credentials, storage
except Exception:  # pragma: no cover - optional dependency
    firebase_admin = None
    credentials = None
    storage = None


@lru_cache(maxsize=1)
def _firebase_bucket():
    if not firebase_admin or not settings.firebase_credentials or not settings.firebase_bucket:
        return None
    bucket_name = settings.firebase_bucket
    if bucket_name.startswith("gs://"):
        bucket_name = bucket_name[5:]
    bucket_name = bucket_name.rstrip("/")
    credentials_path = Path(settings.firebase_credentials)
    if not credentials_path.is_absolute():
        credentials_path = Path(__file__).resolve().parent.parent / credentials_path
    if not firebase_admin._apps:
        cred = credentials.Certificate(str(credentials_path))
        firebase_admin.initialize_app(cred, {"storageBucket": bucket_name})
    return storage.bucket()


def _extension_from_filename(filename: str) -> str:
    if not filename or "." not in filename:
        return ""
    return "." + filename.rsplit(".", 1)[-1].lower()


def save_upload(file: UploadFile, folder: str) -> tuple[str, str]:
    """
    Returns (public_url, storage_type) where storage_type is 'firebase' or 'local'.
    """
    ext = _extension_from_filename(file.filename or "")
    filename = f"{uuid.uuid4().hex}{ext}"

    bucket = _firebase_bucket()
    if bucket:
        blob = bucket.blob(f"{folder}/{filename}")
        content = file.file.read()
        blob.upload_from_string(content, content_type=file.content_type)
        blob.make_public()
        return blob.public_url, "firebase"

    uploads_dir = Path(__file__).resolve().parent / "static" / "uploads" / folder
    uploads_dir.mkdir(parents=True, exist_ok=True)
    dest = uploads_dir / filename
    with dest.open("wb") as buffer:
        buffer.write(file.file.read())
    public_url = f"/static/uploads/{folder}/{filename}"
    return public_url, "local"
