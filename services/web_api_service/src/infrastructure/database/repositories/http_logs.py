from typing import Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.domain.models import HttpLogRecord, HttpLogStats, LogFilters, ParsedHttpLog
from src.core.repositories import AbstractHttpLogRepository
from src.infrastructure.database.mappers import http_log_db_to_domain
from src.infrastructure.database.models import HttpLogModel

class HttpLogRepository(AbstractHttpLogRepository):
    def __init__(self, session: AsyncSession)->None:
        self._session=session

    async def create(self, log: ParsedHttpLog):
        db_log=HttpLogModel(
            ip=log.ip,
            method=log.method,
            uri=log.uri,
            status_code=log.status_code,
            raw_log=log.raw_log,
        )
        self._sesssion.add(db_log)
        try:
            await self._sesssion.commit()
        except Exception:
            await self._sesssion.rollback()
            raise
        await self._sesssion.refresh(db_log)
        return http_log_db_to_domain(db_log)
    
    async def list(self, filters: LogFilters)->Sequence[HttpLogRecord]:
        query: Select[tuple[HttpLogModel]]=select(HttpLogModel)

        if filters.method:
            query=query.where(HttpLogModel.method==filters.method.upper())
        if filters.status_code is not None:
            query=query.where(HttpLogModel.status_code==filters.status_code)
        if filters.created_after is not None:
            query=query.where(HttpLogModel.created_at>filters.created_after)
        if filters.created_before is not None:
            query=query.where(HttpLogModel.created_at<filters.created_before)

        order_column=HttpLogModel.created_at.asc()
        if filters.order=="desc":
            order_column=HttpLogModel.created_at.desc()

        query=query.order_by(order_column).limit(filters.limit).offset(filters.offset)
        result=await self._sesssion.execute(query)
        return [http_log_db_to_domain(row) for row in result.scalars().all()]
    
    async def stats(self)->HttpLogStats:
        method_result=await self._sesssion.execute(
            select(HttpLogModel.method, func.count(HttpLogModel.id)).group_by(
                HttpLogModel.method
            )
        )
        statuses_result=await self._sesssion.execute(
            select(HttpLogModel.status_code, func.count(HttpLogModel.id)).group_by(
                HttpLogModel.status_code
            )
        )

        return HttpLogStats(
            methods={method: count for method, count in method_result.all()},
            status_codes={str(code): count for code, count in statuses_result.all()},
        )