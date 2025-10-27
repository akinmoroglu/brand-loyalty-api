from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.db.init_db import init_db
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Initialize with sample data
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

    yield


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Include all API routes
app.include_router(api_router)


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
