import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use /data/dms.db in docker, or a local sqlite file for local dev
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dms.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
