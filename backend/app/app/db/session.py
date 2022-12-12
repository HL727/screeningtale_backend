from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.session import Session

from app.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionScoped: scoped_session = scoped_session(SessionLocal)


@contextmanager
def session_scope():
    try:
        session: Session = SessionScoped()
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
