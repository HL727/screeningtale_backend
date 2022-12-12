from contextlib import contextmanager
from celery import Celery, signals
from celery.schedules import crontab
from time import time
from redis import Redis

from app.config_redis import redis_pool
from app.utils.closing_hours import CLOSING_HOURS


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


app = Celery(
    "worker",
    backend="redis://redis",
    broker="redis://redis",
    include=["app.worker.insert_historical", "app.worker.send_mail"],
)

BUFFER_MINUTES = 5

app.conf.task_routes = ([("app.worker.*", "main-queue")],)

delete_tokens = {
    "delete-verification-tokens": {
        "task": "app.worker.send_mail.delete_verification_token",
        "schedule": 300.0,
        "args": None,
        "options": {"queue": "main-queue", "priority": 3},
    },
    "delete-reset-password-tokens": {
        "task": "app.worker.send_mail.delete_password_reset_token",
        "schedule": 300.0,
        "args": None,
        "options": {"queue": "main-queue", "priority": 3},
    },
}

add_daily_historicals = {
    f"add-daily-historicals-{d['countries'][0]}": {
        "task": "app.worker.insert_historical.insert_all_historicals",
        "schedule": crontab(
            day_of_week="1-5",
            hour=d["hour"] if d["minute"] + BUFFER_MINUTES < 60 else d["hour"] + 1,
            minute=(d["minute"] + BUFFER_MINUTES) % 60,
            nowfun=d["nowfun"],
        ),
        "args": [d["countries"], 6],
        "options": {"queue": "main-queue", "priority": 6},
    }
    for d in CLOSING_HOURS
}

app.conf.beat_schedule = {**delete_tokens, **add_daily_historicals}
app.conf.beat_schedule = {**delete_tokens}

app.conf.broker_transport_options = {
    "priority_steps": list(range(10)),
    "queue_order_strategy": "priority",
}

d = {}


@signals.task_prerun.connect
def task_prerun_handler(signal, sender, task_id, task, args, **kwargs):
    d[task_id] = time()


@signals.task_postrun.connect
def task_postrun_handler(
    signal, sender, task_id, task, args, kwargs, retval, state, **extras
):
    try:
        start_time = d.pop(task_id)
        cost = time() - start_time
        with sync_redis() as r:
            r.xadd(
                name="task-stats",
                fields={
                    "task_name": task.__name__,
                    "task_id": task_id,
                    "t": cost,
                    "dt": start_time,
                },
            )
    except KeyError:
        cost = -1
