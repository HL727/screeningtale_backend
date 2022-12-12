import types
from typing import Callable, Dict, Optional, Tuple

from aioredis.client import Redis
from app import models, schemas
from app.api.dependencies import reusable_oauth2
from app.config import settings
from app.core import security
from app.db.session import session_scope
from fastapi import HTTPException, Request, Response, status
from fastapi.routing import APIRoute
from jose import jwt
from pydantic import ValidationError


class Limits:
    default: Tuple[int, int] = (5, 1)

    endpoints: Dict[str, Tuple[int, int]] = {
        "historical_performance_view": {
            "FREE": (3, 60 * 60 * 24),
            "PREMIUM": (100, 60 * 60 * 24),
            "ELITE": (1000, 60 * 60 * 24)
        },
    }

    webhook_endpoints = (
        "webhook_handler" 
    )

    def _get_value(self, function_name: str, member_role: str, tuple_index: int) -> int:
        if (
            function_name in self.endpoints
            and member_role
            and len(self.endpoints[function_name]) == 3
            and type(self.endpoints[function_name][member_role][tuple_index]) == int
        ):
            return self.endpoints[function_name][member_role][tuple_index]
        else:
            return self.default[tuple_index]

    def limit(self, function_name: str, member_role: Optional[str] = None) -> int:
        return self._get_value(function_name, member_role, 0)

    def time(self, function_name: str, member_role: Optional[str] = None) -> int:
        return self._get_value(function_name, member_role, 1)


limits = Limits()


class RateLimitAPIRoute(APIRoute):
    """
    Custom `router_class` for automatic ratelimiting of all activity.

    Example usage:
        >>> from fastapi import APIRouter
        >>> from app.* import RateLimitAPIRoute
        >>> router = APIRouter(prefix="/api", route_class=UserActivityLoggingRoute)
    """

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:

            limiter = RateLimit(request)
            await limiter.limit()

            response: Response = await original_route_handler(request)
            return response

        return custom_route_handler


class RateLimit:
    request: Request
    function_name: str
    ip_address: str
    redis: Redis
    redis_key: str
    user_id: Optional[int] = None

    def __init__(self, request: Request):
        self.request = request
        self.function_name = (
            request.scope["endpoint"].__name__
            if type(request.scope["endpoint"]) == types.FunctionType
            else "not_impl"
        )
        self.ip_address = request.client.host
        self.redis = Redis(
            connection_pool=request.app.state.redis_pool,
            encoding="utf-8",
            decode_responses=True,
            client_name="FastAPI-Ratelimiter",
        )
        self.redis_key = f"lim;{self.function_name};{self.ip_address}"

    async def limit(self):
        if self.request.headers.get("Authorization"):
            self.user_id = await self.get_user_id()
        if self.function_name in limits.endpoints:
            await self.rate_limit()
        elif self.function_name in limits.webhook_endpoints:
            pass
        else:
            await self.rate_limit_anonymous()
        await self.redis.close()

    async def rate_limit(self):
        """
        Returns the limit for endpoints given that the user is authenticated
        """
        if self.user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Login required to access this functionality",
            )
        limit = await self.get_limit_by_access_token()
        if int(limit) <= 0:
            with session_scope() as db:
                user = db.query(
                    models.User
                ).filter(models.User.id == self.user_id).first()

                limit = limits.limit(self.function_name, user.member_role)
                time = limits.time(self.function_name, user.member_role)

                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Max {limit} requests per {time} seconds",
                )
        else:
            await self.redis.decr(name=self.redis_key)
        return {"Remaining requests": int(limit) - 1}

    async def get_limit_by_access_token(self) -> Optional[int]:
        """
        Steps:
        - Check if token is in redis-cache
            - If not in cache -> Lookup in database
                - Check if token in sessions
                - Check if sessions.user_id is in users
                - Update cache with result
            - If in cache -> use result from cache
        """
        key = f"token:{self.user_id}"
        user_limit_by_id: Optional[int] = await self.redis.get(name=key)

        if not user_limit_by_id:  # Missing in cache -> need to lookup in database
            with session_scope() as db:
                user = (
                    db.query(
                        models.User
                        ).filter(models.User.id == self.user_id).first()
                )
                if user is None:
                    return 0

                limit = limits.limit(self.function_name, user.member_role)
                time = limits.time(self.function_name, user.member_role)

                print("INVOKED DATABASE")
            # Update Cache
            await self.redis.setex(
                name=key, time=time, value=limit,
            )
            return limit
        else:
            await self.redis.decr(name=key)
            return int(user_limit_by_id)-1

    async def rate_limit_anonymous(self) -> None:
        """
        Returns Rate limit for anonymous functions and user ip based
        """
        limit = await self.redis.get(name=self.redis_key)

        if limit is None:
            await self.redis.setex(
                name=self.redis_key,
                time=limits.time("anonymous"),
                value=limits.limit("anonymous")-1,
            )
        elif int(limit) <= 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests",
            )
        else:
            await self.redis.decr(name=self.redis_key)

    async def get_user_id(self) -> Optional[int]:
        try:
            token = await reusable_oauth2(self.request)
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
            )
            token_data = schemas.TokenPayload(**payload)
        except (jwt.JWTError, ValidationError) as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
        return token_data.sub

    def __repr__(self):
        return f"{self.redis_key}"
