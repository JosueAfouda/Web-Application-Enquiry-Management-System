from __future__ import annotations

from contextvars import ContextVar

_DEFAULT_VALUE = "-"

_request_id_ctx: ContextVar[str] = ContextVar("request_id", default=_DEFAULT_VALUE)
_user_id_ctx: ContextVar[str] = ContextVar("user_id", default=_DEFAULT_VALUE)


def set_request_id(request_id: str | None) -> None:
    _request_id_ctx.set(request_id or _DEFAULT_VALUE)


def set_user_id(user_id: str | None) -> None:
    _user_id_ctx.set(user_id or _DEFAULT_VALUE)


def get_request_id() -> str:
    return _request_id_ctx.get()


def get_user_id() -> str:
    return _user_id_ctx.get()


def clear_request_context() -> None:
    set_request_id(None)
    set_user_id(None)
