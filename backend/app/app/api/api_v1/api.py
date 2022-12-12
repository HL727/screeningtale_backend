from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    optimize_screener,
    stocks,
    stripe_payment,
    test,
    users,
)

api_router = APIRouter()
api_router.include_router(test.router, prefix="/test", tags=["Test"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(
    optimize_screener.router, prefix="/optimize", tags=["Optimize"]
)
api_router.include_router(stripe_payment.router, prefix="/payment", tags=["Payment"])
