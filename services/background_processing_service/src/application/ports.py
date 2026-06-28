from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from typing import Sequence

from src.core.domain.models import ExportState, RemoteHttpLogRecord

class RemoteLogReader(ABC):
    @abstractmethod
    def fetch_logs(
        self,
        *,
        created_after: str|None,
        limit: int
    )->Sequence[RemoteHttpLogRecord]:...

class ExportWriter(ABC):
    @abstractmethod
    def append(self, records: Sequence[RemoteHttpLogRecord])->None: ...

class ExportStateStore(ABC):
    @abstractmethod
    def save(self, state: ExportState)->None: ...

class ExportLock(ABC):
    @abstractmethod
    def acquire(self)->AbstractContextManager[None]: ...