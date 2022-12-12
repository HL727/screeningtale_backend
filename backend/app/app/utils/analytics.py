import time

from aioredis.client import Redis
from fastapi import Request, Response


async def analytics(
    request: Request,
    response: Response,
    start_time: int,
) -> None:
    """
    Helper function to put analysis-data into key-value store
    """
    try:
        end_time = time.time()
        index = hash(f"{request.client.host}{start_time}")
        analytics = {
            "pt": end_time - start_time,
            "st": start_time,
            "ip": anonymize_ip(request.client.host),
            "url": request.url._url,
            "stc": response.status_code,
        }
        r = Redis(
            connection_pool=request.app.state.redis_pool,
            encoding="utf-8",
            decode_responses=True,
            client_name="FastAPI-Analytics",
        )
        # O(n) per operation, where n is the amount of fields.
        import json

        await r.hset(name="analytics", key=index, value=json.dumps(analytics))
    except Exception as err:
        print(err)


def anonymize_ip(ip_address: str) -> str:
    """
    Remove last octet of IP-address

    Formats from `192.14.1.25` to `192.14.1.0`
    """
    try:
        return ip_address[0 : ip_address.rindex(".")] + ".0"
    except Exception:
        return ""
