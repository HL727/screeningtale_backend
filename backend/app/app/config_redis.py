from contextlib import contextmanager
from aioredis import ConnectionPool, Redis
from redis import ConnectionPool as SyncConnectionPool
from redis import Redis as SyncRedis


async def init_redis_pool() -> Redis:
    pool = ConnectionPool(max_connections=100).from_url("redis://redis")
    return pool


def init_sync_redis_pool() -> SyncRedis:
    redis_pool = SyncConnectionPool(max_connections=100).from_url("redis://redis")
    return redis_pool


redis_pool = init_sync_redis_pool()


@contextmanager
def sync_redis():
    r: Redis
    try:
        r: Redis = Redis(connection_pool=redis_pool)
        yield r
    except:
        raise
    finally:
        r.close()
