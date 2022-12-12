from typing import Generator

import aioredis
import pytest
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def db() -> Generator:
    yield SessionLocal()


@pytest.fixture
def client(db, r) -> Generator:
    from app.api.dependencies import get_db, get_redis

    def override_get_db():
        yield db

    def override_get_redis():
        yield r

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def create_redis() -> Generator:
    pool = aioredis.ConnectionPool(max_connections=100).from_url("redis://redis")
    yield pool
    await pool.disconnect(inuse_connections=True)


@pytest.fixture(scope="function")
async def r(create_redis) -> Generator:
    redis = aioredis.Redis(connection_pool=create_redis, decode_responses=True)
    yield redis
    await redis.flushdb()
    await redis.close()
