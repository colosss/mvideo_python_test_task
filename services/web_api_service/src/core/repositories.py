from abc import ABC, abstractmethod
from typing import Sequence

from src.core.domain.models import (
    HttpLogRecord,
    HttpLogStats,
    LogFilters,
    ParsedHttpLog,
)

class AbstractHttpLogRepositories(ABC):
    @abstractmethod
    async def create(self, log: ParsedHttpLog)-> HttpLogRecord: ...

    @abstractmethod
    async def list(self, filters: LogFilters)->Sequence[HttpLogRecord]: ...

    @abstractmethod
    async def stats(self)->HttpLogStats: ...