from contextlib import contextmanager
from typing import Generator

from aioredis import Redis
from fastapi import Request, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm.session import Session

from app.db.session import SessionScoped
from app import models, schemas, crud
from app.config import settings
from app.core import security

reusable_oauth2 = OAuth2PasswordBearer("")


async def get_redis(request: Request) -> Generator:
    try:
        redis = Redis(
            connection_pool=request.app.state.redis_pool,
            encoding="utf-8",
            decode_responses=True,
            client_name="FastAPI",
        )
        yield redis
    finally:
        await redis.close()


def get_db() -> Generator:
    try:
        db: Session = SessionScoped()
        yield db
    finally:
        db.close()


def get_jwt_payload(token: str = Depends(reusable_oauth2)) -> schemas.TokenPayload:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return token_data


def get_current_user(
    token: schemas.TokenPayload = Depends(get_jwt_payload),
    db: Session = Depends(get_db),
) -> models.User:
    user = crud.users.get_user_by_id(token.sub, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
