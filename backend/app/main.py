from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import api_router
from app.core.config import get_settings
from app.core.errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.logging import configure_logging, get_logger
from app.core.request_context import clear_request_context, set_request_id, set_user_id
from app.core.security import TokenError, decode_access_token

settings = get_settings()
configure_logging(settings.app_env)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info(
        "app_startup app_name=%s environment=%s",
        settings.app_name,
        settings.app_env,
    )
    yield
    logger.info("app_shutdown app_name=%s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)
app.include_router(api_router)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


@app.middleware("http")
async def request_context_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id
    set_request_id(request_id)
    set_user_id(None)

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", maxsplit=1)[1].strip()
        try:
            payload = decode_access_token(token)
            sub = payload.get("sub")
            if isinstance(sub, str):
                set_user_id(sub)
        except TokenError:
            pass

    start = perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        duration_ms = round((perf_counter() - start) * 1000, 2)
        logger.info(
            "request_complete method=%s path=%s status=%s duration_ms=%s",
            request.method,
            request.url.path,
            status_code,
            duration_ms,
        )
        clear_request_context()


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}
