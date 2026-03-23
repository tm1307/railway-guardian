from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from ..models.models import Base

# Default to SQLite for ease of simulation / local dev
# Can be overridden by DATABASE_URL environment variable for PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./railway_guardian.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
