from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

@dataclass(frozen=True)
class ParsedHttpLog:
    ip: str
    method: str
    uri: str
    status_code: int
    raw_log: str

@dataclass(frozen=True)
class HttpLogRecord:
    id: UUID
    created_at: datetime
    ip: str
    method: str
    uri: str
    status_code: int
    raw_log: str

@dataclass(frozen=True)
class HttpLogStats:
    method: dict[str, int]
    status_code: dict[str, int]

@dataclass(frozen=True)
class LogFilters:
    limit: int=100
    offset: int=0
    method: str|None=None
    status_code: str|None=None
    created_after: datetime|None=None
    created_before: datetime|None=None
    order: Literal["asc", "desc"]="desc"