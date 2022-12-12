from typing import Any, List, Tuple

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm.session import Session
from aioredis import Redis

from app.api.dependencies import get_db, get_redis, get_current_user
from app.worker import app as celery_app
from app import models
from app.config import settings

from app.utils.api_route_classes.ratelimit import RateLimitAPIRoute


router = APIRouter(route_class=RateLimitAPIRoute)


@router.get("/healthcheck", status_code=200)
def test_me() -> Any:
    """
    Test router endpoint.
    """
    return {"Service": "OK"}


@router.get("/limited_route/{value}", include_in_schema=settings.IS_DEV)
async def get_limit(value: str):
    return {"Hello": "ok"}


@router.get(
    "/test-celery/insert-screener/{ticker}",
    status_code=200,
    include_in_schema=settings.IS_DEV,
)
def test_celery(ticker: str) -> Any:
    """
    Test Celery worker. Insert screener.
    """
    res: AsyncResult = celery_app.send_task(
        "app.worker.insert_historical.insert_screener", args=[ticker]
    )
    return {"msg": "Ticker received", "Task ID": res.id}


@router.get(
    "/test-celery/insert-historical/{ticker}",
    status_code=200,
    include_in_schema=settings.IS_DEV,
)
def test_celery_insert_historical(ticker: str) -> Any:
    """
    Test Celery worker. Insert screener.
    """
    res: AsyncResult = celery_app.send_task(
        "app.worker.insert_historical.insert_historical", args=[ticker]
    )
    return {"msg": "Ticker received", "Task ID": res.id}


@router.get("/ticker-stats", status_code=200)
def get_ticker_stats(db: Session = Depends(get_db)) -> Any:
    """
    Test router endpoint.
    """
    historicals: List[models.Historical] = db.query(models.Historical).distinct(
        models.Historical.ticker
    )
    existing_historicals = [historical.ticker for historical in historicals]
    screener_tickers: List[models.ScreeningTicker] = db.query(
        models.ScreeningTicker
    ).distinct(models.ScreeningTicker.ticker)
    existing_screener_tickers = [
        screener_ticker.ticker for screener_ticker in screener_tickers
    ]
    return {
        "historicals": len(existing_historicals),
        "screener_tickers": len(existing_screener_tickers),
    }


@router.get("/screening_ticker", status_code=200, include_in_schema=settings.IS_DEV)
def get_screening_tickers(db: Session = Depends(get_db)) -> Any:
    """
    Test router endpoint.
    """
    screening_tickers = db.query(models.ScreeningTicker).all()
    tickers = [_obj.ticker for _obj in screening_tickers]
    return {"screening_tickers_amount": len(tickers), "screening_tickers": tickers}


@router.get("/celery", status_code=200, include_in_schema=settings.IS_DEV)
async def get_celery_info(r: Redis = Depends(get_redis)) -> Any:
    """
    Test router endpoint.
    """
    insp = celery_app.control.inspect()
    len_queue = await r.llen(name="main-queue")
    return {"tasks_in_queue": len_queue, "info": insp.stats()}


@router.get(
    "/celery/{task_id: str}", status_code=200, include_in_schema=settings.IS_DEV
)
async def get_celery_task(task_id: str, r: Redis = Depends(get_redis)) -> Any:
    """
    Test router endpoint.
    """
    key = (
        task_id
        if task_id.startswith("celery-task-meta-")
        else f"celery-task-meta-{task_id}"
    )
    task_bytes = await r.get(key)
    if not task_bytes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    import json

    task = json.loads(task_bytes)
    return task


@router.get("/celery-avg-task-time", status_code=200, include_in_schema=settings.IS_DEV)
async def get_celery_task_avg_time(r: Redis = Depends(get_redis)) -> Any:
    """
    Test router endpoint.
    """
    import numpy
    from datetime import datetime

    encoding = "utf-8"
    key = f"task-stats"
    tasks: List[Tuple[bytes, bytes]] = await r.xrevrange(key)
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No tsks in 'task-stats'"
        )

    try:
        newest = float(tasks[0][1][b"dt"].decode(encoding))
        oldest = float(tasks[-1][1][b"dt"].decode(encoding))

        newest = datetime.fromtimestamp(newest)
        oldest = datetime.fromtimestamp(oldest)
    except Exception:
        newest = datetime.utcnow()
        oldest = datetime.utcnow()

    tasks = [float(val[1][b"t"].decode(encoding)) for val in tasks]

    return {
        "avg_process_time": numpy.mean(tasks),
        "datapoints": len(tasks),
        "newest_datapoint": newest.isoformat(),
        "oldest_datapoint": oldest.isoformat(),
        "timespan": str(newest - oldest),
    }


@router.get("/celery-get-tasks", status_code=200, include_in_schema=settings.IS_DEV)
async def get_celery_tasks(r: Redis = Depends(get_redis)) -> Any:
    """
    Test router endpoint.
    """
    encoding = "utf-8"
    key = f"task-stats"
    tasks = []
    async for task in r.scan_iter(match="celery-task-meta-*"):
        tasks.append(task.decode(encoding))
    return tasks


@router.get("/get-current-user")
async def get_current_user_test(user: models.User = Depends(get_current_user)):
    return user


@router.post("/init-db", include_in_schema=settings.IS_DEV)
async def pre_seed_db(db: Session = Depends(get_db)):
    from app.db.pre_seed_db import init_db

    init_db(db, add_h_tick=False)
    return {"status": "ok"}
