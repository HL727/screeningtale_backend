from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.config_redis import init_redis_pool

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
async def startup_event():
    """
    On startup
    - Initialize `Redis` connectionpool
    """
    app.state.redis_pool = await init_redis_pool()


@app.on_event("shutdown")
async def shutdown_event():
    """
    On shutdown
    - Remove `Redis` connectionpool
    """
    await app.state.redis_pool.disconnect(inuse_connections=True)


from app.api.api_v1.api import api_router


app.include_router(api_router, prefix=settings.API_V1_STR)
