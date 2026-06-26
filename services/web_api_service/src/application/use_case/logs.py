from typing import Sequence

from src.application.dto.logs import CreateDTO
from src.application.log_parser import parse_http_log_line
from src.core.domain.models import HttpLogRecord, HttpLogStats, LogFilters
from src.core.repositories import AbstractHttpLogRepositories

class CreateHttpLogUseCase:
    def __init__(self, logs: AbstractHttpLogRepositories)->None:
        self._logs=logs
    
    async def execute(
            self,
            dto: CreateDTO,
    )->HttpLogRecord:
        parsed_log=parse_http_log_line(dto.log)
        return await self._logs.create(parsed_log)
    
class ListHttpLogsUseCase:
    def __init__(self, logs: AbstractHttpLogRepositories)->None:
        self._logs=logs
    
    async def execute(
            self,
            filters: LogFilters,
    )->Sequence[HttpLogRecord]:
        return await self._logs.list(filters)
    
class GetHttpLogsUseCase:
    def __init__(self, logs: AbstractHttpLogRepositories)->None:
        self._logs=logs

    async def execute(self)->HttpLogStats:
        return await self._logs.stats()