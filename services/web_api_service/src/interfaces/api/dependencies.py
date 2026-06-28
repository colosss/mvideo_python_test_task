from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_case.logs import (
    CreateHttpLogUseCase,
    GetHttpLogStatsUseCase,
    ListHttpLogsUseCase,
)
from src.core.repositories import AbstractHttpLogRepository
from src.infrastructure.database.db_helper import db_helper
from src.infrastructure.database.repositories.http_logs import HttpLogRepository

def get_http_log_repository(
        session: Annotated[AsyncSession, Depends(db_helper.session_dependency)],
)->AbstractHttpLogRepository:
    return HttpLogRepository(session)

def get_create_log_use_case(
    repository: Annotated[
        AbstractHttpLogRepository,
        Depends(get_http_log_repository),
    ],
)->CreateHttpLogUseCase:
    return CreateHttpLogUseCase(repository)

def get_list_logs_use_case(
    repository: Annotated[
        AbstractHttpLogRepository,
        Depends(get_http_log_repository),
    ],
)->ListHttpLogsUseCase:
    return ListHttpLogsUseCase(repository)

def get_stats_use_case(
    repository: Annotated[
        AbstractHttpLogRepository,
        Depends(get_http_log_repository),
    ],
)->GetHttpLogStatsUseCase:
    return GetHttpLogStatsUseCase(repository)