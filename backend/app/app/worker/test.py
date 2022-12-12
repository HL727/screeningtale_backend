from celery.utils.log import get_task_logger

from app.worker import app

logger = get_task_logger(__name__)


@app.task(acks_late=True)
def test_celery(word: str) -> str:
    logger.info("Starting initial task")
    return f"Celery test task return, I am new {word}"


@app.task(acks_late=True)
def daily_task() -> str:
    logger.info(f"Starting daily task")
    return f"A daily task!"

