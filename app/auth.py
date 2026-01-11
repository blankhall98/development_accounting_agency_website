from __future__ import annotations

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models import Admin

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def get_admin_from_session(db: Session, admin_id: int | None) -> Admin | None:
    if not admin_id:
        return None
    return db.query(Admin).filter(Admin.id == admin_id).first()
