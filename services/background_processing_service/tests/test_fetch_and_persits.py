from contextlib import nullcontext
import unittest

from src.application.ports import (
    ExportLock,
    ExportStateStore,
    ExportWriter,
    RemoteLogReader,
)
from src.application.use_cases import FetchAndPersistLogsUseCase
from src.core.domain.models import ExportState, RemoteHttpLogRecord

class FakeReader(RemoteLogReader):
    def fetch_logs(self, *, created_after: str|None, limit: int):
        return [
            RemoteHttpLogRecord(
                id="1",
                created="2026-01-01T00:00:00+00:00",
                log={"ip": "192.168.1.1", "method": "GET", "uri": "/", "status_code": 200},
            )
        ]
    
class FakeWriter(ExportWriter):
    def __init__(self) -> None:
        self.records = []

    def append(self, records):
        self.records.extend(records)


class FakeStateStore(ExportStateStore):
    def __init__(self) -> None:
        self.state = ExportState()

    def load(self) -> ExportState:
        return self.state
    
    def save(self, state: ExportState) -> None:
        self.state = state


class FakeLock(ExportLock):
    def acquire(self):
        return nullcontext()


class FetchAndPersistLogsUseCaseTestCase(unittest.TestCase):
    def test_exports_records_and_updates_state(self) -> None:
        writer = FakeWriter()
        state_store = FakeStateStore()
        use_case = FetchAndPersistLogsUseCase(
            reader=FakeReader(),
            writer=writer,
            state_store=state_store,
            export_lock=FakeLock(),
            batch_limit=100,
        )
        
        exported_count = use_case.execute()

        self.assertEqual(exported_count, 1)
        self.assertEqual(len(writer.records), 1)
        self.assertEqual(state_store.state.last_created, "2026-01-01T00:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
