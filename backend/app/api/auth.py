from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.rbac import Roles, require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    TokenPairResponse,
    UserInfo,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db=db)


@router.post("/login", response_model=TokenPairResponse)
def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenPairResponse:
    return service.login(payload)


@router.post("/refresh", response_model=TokenPairResponse)
def refresh(
    payload: RefreshRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenPairResponse:
    return service.refresh(payload.refresh_token)


@router.post("/logout", response_model=MessageResponse)
def logout(
    payload: LogoutRequest,
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    service.logout(payload.refresh_token)
    return MessageResponse(message="logged out")


@router.get("/me", response_model=UserInfo)
def me(
    current_user: User = Depends(
        require_roles(
            Roles.BD,
            Roles.ADMIN,
            Roles.SUPER_ADMIN,
            Roles.SUPPLY_CHAIN,
        )
    ),
) -> UserInfo:
    return UserInfo(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        roles=[role.name for role in current_user.roles],
    )


@router.get("/admin/ping", response_model=MessageResponse)
def admin_ping(
    _: User = Depends(require_roles(Roles.ADMIN, Roles.SUPER_ADMIN)),
) -> MessageResponse:
    return MessageResponse(message="admin access granted")
