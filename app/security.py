import hashlib
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from app.config import get_settings


def hash_password(password: str) -> str:
    prepared = _prepare_password(password)
    return bcrypt.hashpw(prepared, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(_prepare_password(plain_password), hashed_password.encode("utf-8"))


def create_access_token(user_id: UUID) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> UUID | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
    if payload.get("type") != "access" or not payload.get("sub"):
        return None
    try:
        return UUID(str(payload["sub"]))
    except ValueError:
        return None


def new_refresh_token() -> str:
    return token_urlsafe(48)


def new_share_token() -> str:
    return token_urlsafe(32)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def fingerprint_hash(raw_fingerprint: str | None) -> str | None:
    if not raw_fingerprint:
        return None
    return hashlib.sha256(raw_fingerprint.encode("utf-8")).hexdigest()


def _prepare_password(password: str) -> bytes:
    return hashlib.sha256(password.encode("utf-8")).hexdigest().encode("utf-8")
