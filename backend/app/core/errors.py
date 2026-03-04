from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger
from app.core.request_context import get_request_id

logger = get_logger(__name__)


def _request_id_from_request(request: Request) -> str:
    state_request_id = getattr(request.state, "request_id", None)
    if isinstance(state_request_id, str) and state_request_id:
        return state_request_id
    return get_request_id()


def _message_and_details(detail: Any) -> tuple[str, Any | None]:
    if isinstance(detail, str):
        return detail, None
    if isinstance(detail, dict):
        if "message" in detail and isinstance(detail["message"], str):
            details = {k: v for k, v in detail.items() if k != "message"}
            return detail["message"], details or None
        return "request failed", detail
    if isinstance(detail, Sequence):
        return "request failed", detail
    return "request failed", None


def _build_error_payload(
    *,
    code: str,
    message: str,
    request_id: str,
    details: Any | None = None,
) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
            "details": details,
        }
    }


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, HTTPException | StarletteHTTPException):
        return await unhandled_exception_handler(request, exc)

    request_id = _request_id_from_request(request)
    message, details = _message_and_details(exc.detail)
    payload = _build_error_payload(
        code=f"http_{exc.status_code}",
        message=message,
        request_id=request_id,
        details=details,
    )
    logger.warning(
        "http_exception status=%s method=%s path=%s",
        exc.status_code,
        request.method,
        request.url.path,
    )
    response = JSONResponse(
        status_code=exc.status_code,
        content=payload,
        headers=exc.headers,
    )
    response.headers["X-Request-ID"] = request_id
    return response


async def validation_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, RequestValidationError):
        return await unhandled_exception_handler(request, exc)

    request_id = _request_id_from_request(request)
    payload = _build_error_payload(
        code="validation_error",
        message="request validation failed",
        request_id=request_id,
        details=exc.errors(),
    )
    logger.warning(
        "validation_exception method=%s path=%s",
        request.method,
        request.url.path,
    )
    response = JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=payload,
    )
    response.headers["X-Request-ID"] = request_id
    return response


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = _request_id_from_request(request)
    logger.exception(
        "unhandled_exception method=%s path=%s",
        request.method,
        request.url.path,
    )
    payload = _build_error_payload(
        code="internal_server_error",
        message="internal server error",
        request_id=request_id,
        details=None,
    )
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=payload,
    )
    response.headers["X-Request-ID"] = request_id
    return response
