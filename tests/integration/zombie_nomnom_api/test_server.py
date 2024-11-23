import json
import httpx
import pytest
from fastapi.testclient import TestClient
from zombie_nomnom_api import configs


def test_api__when_requesting_health_check__returns_ok(api_client: TestClient):
    response: httpx.Request = api_client.get("/healthz")
    value = json.loads(response.content)
    assert value == {"o": "k"}


def test_cors_function_for_api(api_client: TestClient):
    response: httpx.Request = api_client.get(
        "/healthz", headers={"origin": "http://localhost:3000"}
    )
    assert response.headers.get("access-control-allow-origin") == "*"


def test_version__when_requesting_version__returns_object_with_version_field(
    api_client: TestClient,
):
    response: httpx.Request = api_client.get("/version")
    value = json.loads(response.content)
    assert "version" in value
    assert value["version"]


@pytest.mark.asyncio
async def test_mongo_communication():
    sut = configs.mongo_client()

    await sut[configs.game_collection].find_one({})