import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.db.session import engine

# Quick test (no schemas / routes needed yet)
from fastapi import Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This needs to be changed to lifespan
# @app.on_event("startup")
# def startup_db_check() -> None:
#     # Connect once and run a trivial query to verify DB connectivity.
#     with engine.connect() as conn:
#         conn.execute(text("SELECT 1"))
#     logging.info("DB connection OK")
#     # logger.info("DB connection OK")   # Test 2

# Lifespan version
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("DB connection OK")
    yield  # App runs here

    # SHUTDOWN (we don't need anything yet, but later we could close resources)
    # logger.info("Shutting down...")

# app = FastAPI(title=settings.APP_NAME)    # Changed because of the lifespan
app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)


# Methode for the Quick test
@app.get("/db/ping")
def db_ping(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"ok": True}

app.include_router(v1_router, prefix="/api/v1")
