from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


_engine: Engine | None = None
_session_local: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        database_url = get_settings().database_url
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        _engine = create_engine(database_url, pool_pre_ping=True, connect_args=connect_args)
    return _engine


def get_session_local() -> sessionmaker[Session]:
    global _session_local
    if _session_local is None:
        _session_local = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False, expire_on_commit=False)
    return _session_local


def get_db() -> Generator[Session, None, None]:
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()


def init_local_database() -> None:
    if get_settings().database_url.startswith("sqlite"):
        Base.metadata.create_all(bind=get_engine())
