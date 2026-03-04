import asyncio
import json

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request

from app.core.errors import http_exception_handler, validation_exception_handler


def _build_request(path: str, method: str = "GET", request_id: str = "test-req-id") -> Request:
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("utf-8"),
        "query_string": b"",
        "headers": [],
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }
    request = Request(scope)
    request.state.request_id = request_id
    return request


def test_validation_error_has_consistent_schema() -> None:
    request = _build_request("/dummy", method="POST")
    exc = RequestValidationError(
        [
            {
                "loc": ("body", "username"),
                "msg": "Field required",
                "type": "missing",
            }
        ]
    )

    response = asyncio.run(validation_exception_handler(request, exc))
    assert response.status_code == 422
    assert response.headers.get("X-Request-ID") == "test-req-id"

    payload = json.loads(response.body.decode("utf-8"))
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["message"] == "request validation failed"
    assert payload["error"]["request_id"] == "test-req-id"


def test_http_error_has_consistent_schema() -> None:
    request = _build_request("/dummy")
    exc = HTTPException(status_code=401, detail="Not authenticated")

    response = asyncio.run(http_exception_handler(request, exc))
    assert response.status_code == 401
    assert response.headers.get("X-Request-ID") == "test-req-id"

    payload = json.loads(response.body.decode("utf-8"))
    assert payload["error"]["code"] == "http_401"
    assert payload["error"]["message"] == "Not authenticated"
    assert payload["error"]["request_id"] == "test-req-id"
