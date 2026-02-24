from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Engine = the “database connection factory” for SQLAlchemy.
# It is created once and reused.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# SessionLocal = factory for DB sessions (transactions).
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
