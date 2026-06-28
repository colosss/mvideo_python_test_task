from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from src.application.use_case.logs import GetHttpLogStatsUseCase
from src.interfaces.api.dependencies import get_stats_use_case
from src.interfaces.api.schemas import StatsSchema, stats_to_schema

router=APIRouter(prefix="/api/stats", tags=["Stats"])

@router.get("", response_model=StatsSchema)
async def get_stats(
    use_case: Annotated[GetHttpLogStatsUseCase, Depends(get_stats_use_case)],
)->StatsSchema:
    try:
        stats=await use_case.execute()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "STORAGE_ERROR",
                    "message": "Could not calculate stats",
                }
            },
        ) from exc
    
    return stats_to_schema(stats)