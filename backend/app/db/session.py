import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# Use /data/dms.db in docker, or a local sqlite file for local dev
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dms.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Enable WAL mode for SQLite so multiple processes (backend, bot, worker)
# can read/write the same database file simultaneously without locking.
if "sqlite" in DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all database tables. Call this from each process entry point."""
    from app.db.base import Base
    from app.db.models.job import Job  # noqa: F401 - Ensure model is registered
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
