import json
from fastapi.testclient import TestClient
import httpx


def test_api__when_requesting_health_check__returns_ok(api_client: TestClient):
    response: httpx.Request = api_client.get("/healthz")
    value = json.loads(response.content)
    assert value == {"o": "k"}


def test_cors_function_for_api(api_client: TestClient):
    response: httpx.Request = api_client.get(
        "/healthz", headers={"origin": "http://localhost:3000"}
    )
    assert response.headers.get("access-control-allow-origin") == "*"
