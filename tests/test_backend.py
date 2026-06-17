from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.schemas import LocationRequest, RegisterRequest
from app.security import create_access_token, decode_access_token, fingerprint_hash, token_hash


def test_app_imports_and_registers_expected_routes():
    paths = set(app.openapi()["paths"])
    websocket_paths = _registered_paths(include_websockets=True)

    assert "/" in paths
    assert "/health" in paths
    assert "/auth/register" in paths
    assert "/auth/login" in paths
    assert "/auth/refresh" in paths
    assert "/sessions/start" in paths
    assert "/track/{share_token}/location" in paths
    assert "/sos" in paths
    assert "/ws/track/{share_token}" in websocket_paths


def _registered_paths(include_websockets: bool = False) -> set[str]:
    paths: set[str] = set()
    routes = list(app.routes)
    for route in app.routes:
        original_router = getattr(route, "original_router", None)
        if original_router is not None:
            routes.extend(original_router.routes)
    for route in routes:
        path = getattr(route, "path", None)
        if path is None:
            continue
        if include_websockets or "websocket" not in type(route).__name__.lower():
            paths.add(path)
    return paths


def test_health_endpoint():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_access_token_round_trip():
    user_id = uuid4()

    token = create_access_token(user_id)

    assert decode_access_token(token) == user_id


def test_hash_helpers_are_stable_and_do_not_expose_raw_values():
    raw = "device-123"

    assert token_hash(raw) == token_hash(raw)
    assert fingerprint_hash(raw) == fingerprint_hash(raw)
    assert token_hash(raw) != raw
    assert fingerprint_hash(raw) != raw


def test_schema_validation_accepts_expected_payloads():
    user = RegisterRequest(name="Amina", email="amina@example.com", password="strong-password")
    location = LocationRequest(latitude=6.5244, longitude=3.3792, accuracy=12)

    assert user.email == "amina@example.com"
    assert location.latitude == 6.5244
