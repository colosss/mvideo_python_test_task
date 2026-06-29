from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError

from src.application.dto.logs import CreateLogDTO
from src.application.log_parser import ALLOWED_HTTP_METHOD, InvalidLogFormatError
from src.application.use_case.logs import CreateHttpLogUseCase,ListHttpLogsUseCase
from src.core.domain.models import LogFilters
from src.interfaces.api.dependencies import (
    get_create_log_use_case,
    get_list_logs_use_case,
)
from src.interfaces.api.schemas import (
    HttpLogRecordSchema,
    LogCreateRequest,
    OrderQuery,
    http_log_record_to_schema,
)

router=APIRouter(prefix="/api/data", tags=["Logs"])

@router.post(
    "",
    response_model=HttpLogRecordSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_log(
    body: LogCreateRequest,
    use_case: Annotated[CreateHttpLogUseCase, Depends(get_create_log_use_case)],
)->HttpLogRecordSchema:
    try:
        record=await use_case.execute(CreateLogDTO(log=body.log))
    except InvalidLogFormatError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_LOG_FORMAT",
                    "message": str(exc),
                }
            },
        ) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "STORAGE_ERROR",
                    "message": "Could not save log record",
                }
            },
        ) from exc
    
    return http_log_record_to_schema(record)

@router.get("", response_model=list[HttpLogRecordSchema])
async def list_logs(
    use_case: Annotated[ListHttpLogsUseCase, Depends(get_list_logs_use_case)],
    limit: Annotated[int, Query(ge=1, le=1000)]=100,
    offset: Annotated[int, Query(ge=0)]=0,
    method: Annotated[str|None, Query()]=None,
    status_code: Annotated[int|None, Query(ge=100, le=599)]=None,
    created_after: Annotated[datetime|None, Query()]=None,
    created_before: Annotated[datetime|None, Query()]=None,
    order: Annotated[OrderQuery, Query()]="desc",
)->list[HttpLogRecordSchema]:
    if method is not None and method.upper() not in ALLOWED_HTTP_METHOD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_QUERY",
                    "message": "Unknown HTTP method filter",
                }
            },
        )
    filters=LogFilters(
        limit=limit,
        offset=offset,
        method=method.upper() if method else None,
        status_code=status_code,
        created_after=created_after,
        created_before=created_before,
        order=order,
    )

    try:
        records=await use_case.execute(filters)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "STORAGE_ERROR",
                    "message": "Could not read log records",
                }
            },
        ) from exc
    
    return [http_log_record_to_schema(record) for record in records]
