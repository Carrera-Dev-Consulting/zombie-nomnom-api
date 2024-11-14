import json
from fastapi.testclient import TestClient
import httpx


def test_api__when_requesting_health_check__returns_ok(api_client: TestClient):
    response: httpx.Request = api_client.get("/healthz")
    value = json.loads(response.content)
    assert value == {"o": "k"}
