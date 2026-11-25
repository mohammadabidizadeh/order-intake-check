"""Read-only, single-business HTTP adapter."""

import logging
import os
import secrets
from email.message import Message
from pathlib import Path
from typing import Annotated

from anyio import fail_after
from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import ClientDisconnect

from . import __version__
from .intake import FileProblem, Preview, check_size, load_catalog, preview, read_limited

log = logging.getLogger("uvicorn.error")
bearer = HTTPBearer(auto_error=False, description="Token issued by the local operator.")
BODY_TIMEOUT_SECONDS = 30


class Problem(BaseModel):
    code: str
    message: str
    record: int | None = None


class RequestProblem(Exception):
    def __init__(self, status: int, code: str, message: str, record: int | None = None):
        self.status = status
        self.body = Problem(code=code, message=message, record=record)


def _is_order_csv(request: Request) -> bool:
    types = request.headers.getlist("content-type")
    encodings = [s.strip().lower() for s in request.headers.getlist("content-encoding")]
    if len(types) != 1 or encodings not in ([], ["identity"]):
        return False
    media = Message()
    media["Content-Type"] = types[0]
    if media.get_content_type() != "text/csv":
        return False
    # Use the full parameter list so conflicting declarations cannot be lost.
    try:
        parameters = media.get_params()[1:]
    except ValueError:
        return False
    for key, value in parameters:
        if key == "charset" and str(value).lower() not in ("utf-8", "utf8"):
            return False
        if key == "header" and str(value).lower() != "present":
            return False
    return True


def create_app() -> FastAPI:
    token = os.environ.get("ORDERCHECK_TOKEN", "")
    if len(token) < 32 or not token.isascii() or not token.isprintable() or any(c.isspace() for c in token):
        raise RuntimeError("Set ORDERCHECK_TOKEN to a random ASCII token of at least 32 characters.")
    catalog_path = os.environ.get("ORDERCHECK_CATALOG")
    if not catalog_path:
        raise RuntimeError("Set ORDERCHECK_CATALOG to an approved catalog CSV.")
    try:
        catalog = load_catalog(read_limited(Path(catalog_path)))
    except (OSError, FileProblem) as exc:
        raise RuntimeError("Unable to load approved catalog: " + getattr(exc, "code", "unreadable")) from None

    app = FastAPI(title="Order Intake Check", version=__version__, docs_url=None, redoc_url=None,
                  description="Preview one reseller order file against the process-local product mapping.")
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])

    @app.exception_handler(RequestProblem)
    async def handle_problem(request: Request, exc: RequestProblem) -> JSONResponse:
        headers = {"Cache-Control": "no-store"}
        if exc.status == 401:
            headers["WWW-Authenticate"] = "Bearer"
        if exc.status in (408, 413) and request.scope["http_version"].startswith("1."):
            headers["Connection"] = "close"
        return JSONResponse(exc.body.model_dump(), status_code=exc.status, headers=headers)

    async def authorize(request: Request,
                        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> None:
        if (credentials is None or len(request.headers.getlist("authorization")) != 1
                or not secrets.compare_digest(credentials.credentials.encode(), token.encode())):
            raise RequestProblem(401, "unauthorized", "A valid local preview token is required.")

    @app.get("/healthz", response_model=dict[str, str], summary="Check process and catalog readiness")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/order-previews", response_model=Preview, dependencies=[Depends(authorize)],
              responses={400: {"model": Problem, "description": "Invalid Host or interrupted upload",
                               "content": {"text/plain": {"schema": {"type": "string"}}}},
                         **{code: {"model": Problem} for code in (401, 408, 413, 415, 422)}},
              openapi_extra={"requestBody": {"required": True, "content": {
                  "text/csv": {"schema": {"type": "string", "description": "UTF-8 CSV with header"}}
              }}}, summary="Check an order file without creating orders")
    async def preview_orders(request: Request, response: Response) -> Preview:
        if not _is_order_csv(request):
            raise RequestProblem(415, "unsupported_media", "Send uncompressed UTF-8 text/csv with a header.")
        body = bytearray()
        try:
            with fail_after(BODY_TIMEOUT_SECONDS):
                async for chunk in request.stream():
                    check_size(len(body) + len(chunk))
                    body.extend(chunk)
            result = await run_in_threadpool(preview, bytes(body), catalog)
        except TimeoutError:
            raise RequestProblem(408, "body_timeout", "The CSV upload exceeded the time limit.") from None
        except ClientDisconnect:
            raise RequestProblem(400, "incomplete_body", "The CSV upload ended early.") from None
        except FileProblem as exc:
            status = 413 if exc.code == "file_too_large" else 422
            raise RequestProblem(status, exc.code, str(exc), exc.record) from None
        response.headers["Cache-Control"] = "no-store"
        log.info("order_preview records=%d ready=%d held=%d", result.records, result.ready_orders, result.held_orders)
        return result

    return app
