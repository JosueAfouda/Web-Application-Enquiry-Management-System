from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.models.user import User


class Roles:
    BD = "BD"
    ADMIN = "Admin"
    SUPER_ADMIN = "SuperAdmin"
    SUPPLY_CHAIN = "SupplyChain"


def require_roles(*allowed_roles: str) -> Callable[[User], User]:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        user_roles = {role.name for role in current_user.roles}
        if not user_roles.intersection(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="insufficient role permissions",
            )
        return current_user

    return dependency
