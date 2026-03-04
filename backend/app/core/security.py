from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()


class TokenError(ValueError):
    """Raised when a JWT token is invalid or malformed."""


def now_utc() -> datetime:
    return datetime.now(UTC)


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(subject: str, roles: list[str]) -> tuple[str, datetime]:
    expires_at = now_utc() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": subject,
        "roles": roles,
        "type": "access",
        "exp": expires_at,
        "iat": now_utc(),
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return token, expires_at


def decode_access_token(token: str) -> dict[str, object]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise TokenError("invalid access token") from exc

    token_type = payload.get("type")
    if token_type != "access":
        raise TokenError("invalid token type")

    if "sub" not in payload:
        raise TokenError("missing token subject")

    return payload


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(refresh_token: str) -> str:
    return hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
