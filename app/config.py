from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Settings:
    app_name: str = os.getenv("APP_NAME", "Agencia Contable")
    secret_key: str = os.getenv("SECRET_KEY", "change-this-secret")
    database_url: str = normalize_database_url(
        os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'app.db'}")
    )

    super_admin_username: str = os.getenv("SUPER_ADMIN_USERNAME", "superadmin")
    super_admin_password: str = os.getenv("SUPER_ADMIN_PASSWORD", "ChangeMe123!")

    smtp_host: Optional[str] = os.getenv("SMTP_HOST")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: Optional[str] = os.getenv("SMTP_USER")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    smtp_from: Optional[str] = os.getenv("SMTP_FROM")

    firebase_credentials: Optional[str] = os.getenv("FIREBASE_CREDENTIALS")
    firebase_bucket: Optional[str] = os.getenv("FIREBASE_BUCKET")

    admin_session_key: str = os.getenv("ADMIN_SESSION_KEY", "admin_session")


settings = Settings()
