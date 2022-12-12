import logging

from app.db.pre_seed_db import init_db
from app.db.session import session_scope

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    with session_scope() as db:
        init_db(db)


def main() -> None:
    logger.info("Preseeding database")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
