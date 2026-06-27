from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import settings

class DataBaseHelper:
    def __init__(self, url: str, echo: bool=False)->None:
        self.engine=create_async_engine(url=url, echo=echo, pool_pre_ping=True)
        self.session_factory=async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
    
    async def session_dependency(self)->AsyncIterator[AsyncSession]:
        async with self.session_factory() as session:
            yield session
        
    async def create_tables(self)->None:
        from src.infrastructure.database.base import Base

        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def dispose(self)->None:
        await self.engine.dispose()

db_helper=DataBaseHelper(settings.database_url, settings.DB_ECHO)