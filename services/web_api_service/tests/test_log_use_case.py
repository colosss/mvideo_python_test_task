from datetime import datetime, timezone
from uuid import uuid4
import unittest

from src.application.dto.logs import CreateLogDTO
from src.application.use_case.logs import CreateHttpLogUseCase, ListHttpLogsUseCase
from src.core.domain.models import HttpLogRecord, LogFilters,ParsedHttpLog
from src.core.repositories import AbstractHttpLogRepository

class FakeHttpLogRepository(AbstractHttpLogRepository):
    def __init__(self)->None:
        self.records: list[HttpLogRecord]=[]

    async def create(self, log: ParsedHttpLog)->HttpLogRecord:
        record=HttpLogRecord(
            id=uuid4(),
            created_at=datetime.now(timezone.utc),
            ip=log.ip,
            method=log.method,
            uri=log.uri,
            status_code=log.status_code,
            raw_log=log.raw_log,
        )
        self.records.append(record)
        return record
    
    async def list(self, filters: LogFilters)->list[HttpLogRecord]:
        return self.records[filters.offset : filters.offset + filters.limit]
    
    async def stats(self):
        raise NotImplementedError
    

class LogUseCaseTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_create_log_use_case_parses_and_stores_record(self)->None:
        repository=FakeHttpLogRepository()
        use_case=CreateHttpLogUseCase(repository)

        record=await use_case.execute(
            CreateLogDTO(log="192.168.1.1 POST /api/orders 201"),
        )
        self.assertEqual(record.method, "POST")
        self.assertEqual(record.status_code, 201)
        self.assertEqual(len(repository.records),1)

    async def test_list_log_use_case_delegates_to_repository(self)->None:
        repository=FakeHttpLogRepository()
        create_use_case=CreateHttpLogUseCase(repository)
        list_use_case=ListHttpLogsUseCase(repository)

        await create_use_case.execute(
            CreateLogDTO(log="192.168.1.1 GET /api/users 200"),
        )

        records=await list_use_case.execute(LogFilters(limit=10))

        self.assertEqual(len(records),1)

if __name__=="__main__":
    unittest.main()