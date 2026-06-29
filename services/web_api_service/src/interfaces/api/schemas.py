from datetime  import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from src.core.domain.models import HttpLogRecord, HttpLogStats

class LogCreateRequest(BaseModel):
    log: str=Field(
        min_length=1,
        examples=["192.168.1.1 GET /api/users 200"],
    )

class LogPayloadSchema(BaseModel):
    ip: str
    method: str
    uri: str
    status_code: int

class HttpLogRecordSchema(BaseModel):
    id: UUID
    created: datetime
    log: LogPayloadSchema

class StatsSchema(BaseModel):
    methods: dict[str, int]
    status_codes: dict[str, int]

class ErrorResponse(BaseModel):
    detail: dict[str, dict[str, str]]

OrderQuery=Literal["asc", "desc"]

def http_log_record_to_schema(record: HttpLogRecord)->HttpLogRecordSchema:
    return HttpLogRecordSchema(
        id=record.id,
        created=record.created_at,
        log=LogPayloadSchema(
            ip=record.ip,
            method=record.method,
            uri=record.uri,
            status_code=record.status_code,
        )
    )

def stats_to_schema(stats: HttpLogStats)->StatsSchema:
    return StatsSchema(method=stats.method, status_code=stats.status_code)