import json
import secrets
from pathlib import Path

import anyio
import httpx
import pytest

from ordercheck.api import create_app
from ordercheck.intake import MAX_BYTES

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
URL = "/v1/order-previews"


@pytest.fixture
def service(monkeypatch):
    token = secrets.token_urlsafe(32)
    monkeypatch.setenv("ORDERCHECK_CATALOG", str(EXAMPLES / "catalog.csv"))
    monkeypatch.setenv("ORDERCHECK_TOKEN", token)
    return create_app(), {"Authorization": f"Bearer {token}", "Content-Type": "text/csv"}


def request(app, method, path, **options):
    async def send():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost") as client:
            return await client.request(method, path, **options)
    return anyio.run(send)


def test_preview_and_health(service):
    app, headers = service
    assert request(app, "GET", "/healthz").json() == {"status": "ok"}
    response = request(app, "POST", URL, headers=headers, content=(EXAMPLES / "orders.csv").read_bytes())
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json()["held_orders"] == 1
    assert response.json()["orders"][1]["lines"] == []


@pytest.mark.parametrize("authorization", [None, "Bearer wrong", "Basic ignored"])
def test_auth_precedes_body_processing(service, authorization):
    app, _ = service
    headers = {} if authorization is None else {"Authorization": authorization}
    result = request(app, "POST", URL, headers=headers, content=b"bad file")
    assert result.status_code == 401
    assert result.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize("extra", [{"Content-Type": "application/json"}, {"Content-Encoding": "gzip"}])
def test_wrong_representation(service, extra):
    app, headers = service
    assert request(app, "POST", URL, headers=headers | extra, content=b"abc").status_code == 415


@pytest.mark.parametrize(("media", "expected"), [
    ('Text/CSV; charset="UTF-8"', 200),
    ("text/csv; charset=iso-8859-1", 415),
    ("text/csv; header=absent", 415),
    ("text/csv; header=present; charset=utf-8", 200),
    ("text/csv; charset=utf-8; charset=ascii", 415),
])
def test_csv_representation_contract(service, media, expected):
    app, headers = service
    result = request(app, "POST", URL, headers=headers | {"Content-Type": media},
                     content=(EXAMPLES / "orders.csv").read_bytes())
    assert result.status_code == expected


def test_body_deadline(service, monkeypatch):
    app, headers = service
    monkeypatch.setattr("ordercheck.api.BODY_TIMEOUT_SECONDS", 0.05)

    async def chunks():
        yield b"order_id,"
        await anyio.sleep(0.15)
        yield b"line_id"

    result = request(app, "POST", URL, headers=headers, content=chunks())
    assert (result.status_code, result.json()["code"]) == (408, "body_timeout")
    assert result.headers["cache-control"] == "no-store"


def test_auth_does_not_read_body(service):
    app, _ = service

    async def body():
        raise AssertionError("Unauthorized body was consumed")
        yield b""

    assert request(app, "POST", URL, content=body()).status_code == 401


def test_structure_error_does_not_echo_source(service):
    app, headers = service
    result = request(app, "POST", URL, headers=headers, content=b"private-note\n")
    assert result.status_code == 422
    assert result.json()["record"] == 1
    assert "private-note" not in result.text


def test_streaming_budget(service):
    app, headers = service
    async def chunks():
        yield b"x" * MAX_BYTES
        yield b"y"
    result = request(app, "POST", URL, headers=headers, content=chunks())
    assert (result.status_code, result.json()["code"]) == (413, "file_too_large")


def test_interrupted_upload(service):
    from starlette.requests import ClientDisconnect

    app, headers = service

    async def chunks():
        yield b"order_id,"
        raise ClientDisconnect()

    result = request(app, "POST", URL, headers=headers, content=chunks())
    assert (result.status_code, result.json()["code"]) == (400, "incomplete_body")


@pytest.mark.parametrize(("field", "value", "status"), [
    ("Authorization", "Bearer other", 401),
    ("Content-Type", "text/plain", 415),
    ("Content-Encoding", "gzip", 415),
])
def test_ambiguous_request_headers(service, field, value, status):
    app, headers = service
    repeated = [*headers.items(), ("Content-Encoding", "identity"), (field, value)]
    result = request(app, "POST", URL, headers=repeated, content=(EXAMPLES / "orders.csv").read_bytes())
    assert result.status_code == status


def test_catalog_is_a_startup_snapshot(monkeypatch, tmp_path):
    path = tmp_path / "catalog.csv"
    path.write_bytes(b"source_sku,item_code\nA,OLD\n")
    token = secrets.token_urlsafe(32)
    monkeypatch.setenv("ORDERCHECK_CATALOG", str(path))
    monkeypatch.setenv("ORDERCHECK_TOKEN", token)
    first = create_app()
    path.write_bytes(b"source_sku,item_code\nA,NEW\n")
    for app, expected in ((first, "OLD"), (create_app(), "NEW")):
        result = request(app, "POST", URL, headers={"Authorization": f"Bearer {token}", "Content-Type": "text/csv"},
                         content=b"order_id,line_id,source_sku,quantity\nO,1,A,2")
        assert result.json()["orders"][0]["lines"][0]["item_code"] == expected


def test_host_restriction(service):
    app, _ = service
    assert request(app, "GET", "/healthz", headers={"Host": "untrusted.local"}).status_code == 400


def test_schema_matches_snapshot(service):
    app, _ = service
    spec = request(app, "GET", "/openapi.json").json()
    assert spec == json.loads((ROOT / "docs/openapi.json").read_bytes())
    operation = spec["paths"][URL]["post"]
    assert operation["security"]
    assert list(operation["requestBody"]["content"]) == ["text/csv"]


def test_no_weak_startup_config(monkeypatch):
    monkeypatch.delenv("ORDERCHECK_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="TOKEN"):
        create_app()


def test_missing_or_invalid_catalog(monkeypatch, tmp_path):
    monkeypatch.setenv("ORDERCHECK_TOKEN", secrets.token_urlsafe(32))
    monkeypatch.delenv("ORDERCHECK_CATALOG", raising=False)
    with pytest.raises(RuntimeError, match="CATALOG"):
        create_app()
    file = tmp_path / "bad.csv"
    file.write_text("source_sku,item_code\nA,B\nA,C")
    monkeypatch.setenv("ORDERCHECK_CATALOG", str(file))
    with pytest.raises(RuntimeError, match="duplicate_mapping"):
        create_app()
