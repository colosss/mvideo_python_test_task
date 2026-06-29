from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.infrastructure.database.db_helper import db_helper
from src.interfaces.api import data, health, stats
from src.interfaces.api.constants import SERVICE_NAME

@asynccontextmanager
async def lifespan(app: FastAPI)->AsyncIterator[None]:
    yield
    await db_helper.dispose()

def create_app()->FastAPI:
    app=FastAPI(title=SERVICE_NAME, lifespan=lifespan)
    app.include_router(health.router)
    app.include_router(data.router)
    app.include_router(stats.router)
    return app