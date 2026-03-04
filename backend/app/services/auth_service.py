from __future__ import annotations

from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
    now_utc,
    verify_password,
)
from app.models.session_token import SessionToken
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenPairResponse, UserInfo

settings = get_settings()


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login(self, payload: LoginRequest) -> TokenPairResponse:
        user = self._authenticate(payload.username, payload.password)
        return self._issue_tokens(user)

    def refresh(self, refresh_token: str) -> TokenPairResponse:
        token_hash = hash_refresh_token(refresh_token)
        session_row = self.db.scalar(
            select(SessionToken)
            .options(selectinload(SessionToken.user).selectinload(User.roles))
            .where(SessionToken.refresh_token_hash == token_hash)
        )

        if session_row is None or session_row.revoked_at is not None:
            raise self._unauthorized("invalid refresh token")

        if session_row.expires_at <= now_utc():
            raise self._unauthorized("refresh token expired")

        if not session_row.user.is_active:
            raise self._unauthorized("user is inactive")

        session_row.revoked_at = now_utc()
        response = self._issue_tokens(session_row.user)
        self.db.commit()
        return response

    def logout(self, refresh_token: str) -> None:
        token_hash = hash_refresh_token(refresh_token)
        session_row = self.db.scalar(
            select(SessionToken).where(SessionToken.refresh_token_hash == token_hash)
        )
        if session_row is not None and session_row.revoked_at is None:
            session_row.revoked_at = now_utc()
            self.db.commit()

    def _authenticate(self, username_or_email: str, password: str) -> User:
        user = self.db.scalar(
            select(User)
            .options(selectinload(User.roles))
            .where(
                or_(
                    User.username == username_or_email,
                    User.email == username_or_email,
                )
            )
        )

        if user is None:
            raise self._unauthorized("invalid credentials")

        if not user.is_active:
            raise self._unauthorized("user is inactive")

        if not verify_password(password, user.password_hash):
            raise self._unauthorized("invalid credentials")

        return user

    def _issue_tokens(self, user: User) -> TokenPairResponse:
        refresh_token = generate_refresh_token()
        refresh_token_hash = hash_refresh_token(refresh_token)
        refresh_expires_at = now_utc() + timedelta(minutes=settings.refresh_token_expire_minutes)

        access_token, access_token_expires_at = create_access_token(
            subject=str(user.id),
            roles=[role.name for role in user.roles],
        )

        self.db.add(
            SessionToken(
                user_id=user.id,
                refresh_token_hash=refresh_token_hash,
                expires_at=refresh_expires_at,
            )
        )
        self.db.commit()

        return TokenPairResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_at=access_token_expires_at,
            user=UserInfo(
                id=str(user.id),
                username=user.username,
                email=user.email,
                is_active=user.is_active,
                roles=[role.name for role in user.roles],
            ),
        )

    @staticmethod
    def _unauthorized(detail: str) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
