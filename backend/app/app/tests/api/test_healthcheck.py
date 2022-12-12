import pytest
from aioredis import Redis
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings


def test_healthcheck(client: TestClient) -> None:
    response = client.get(f"{settings.API_V1_STR}/test/healthcheck")
    assert response.status_code == 200
    content = response.json()
    assert content["Service"] == "OK"


@pytest.mark.asyncio
async def test_aioredis(r: Redis) -> None:
    await r.set(name="some_key", value="some_value")
    response = await r.get(name="some_key")
    assert type(response) == bytes


@pytest.mark.asyncio
async def test_aioredis_2(r: Redis) -> None:
    response = await r.get(name="some_key")
    assert response is None


def test_aioredis_3(client: TestClient) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/test/redis/", json={"key": "banana", "value": "cake"}
    )
    assert response.status_code == 200

    response = client.get(f"{settings.API_V1_STR}/test/redis/banana")
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "banana"
    assert data["value"] == "cake"


def test_aioredis_4(client: TestClient) -> None:
    response = client.get(f"{settings.API_V1_STR}/test/redis/banana")
    assert response.status_code == 404
