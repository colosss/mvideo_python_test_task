from src.application.ports import (
    ExportLock,
    ExportStateStore,
    ExportWriter,
    RemoteLogReader,
)
from src.core.domain.models import ExportState

class FetchAndPersistLogsUseCase:
    def __init__(
        self,
        *,
        reader: RemoteLogReader,
        writer: ExportWriter,
        state_store: ExportStateStore,
        export_lock: ExportLock,
        batch_limit: int,
    )->None:
        self._reader=reader
        self._writer=writer
        self._state_store=state_store
        self._export_lock=export_lock
        self._batch_limit=batch_limit

    def execute(self)->int:
        with self._export_lock.acquire():
            state=self._state_store.load()
            records=list(
                self._reader.fetch_logs(
                    created_after=state.last_created,
                    limit=self._batch_limit,
                )
            )
            if not records:
                return 0
            
            self._writer.append(records)
            self._state_store.save(ExportState(last_created=records[-1].created))
            return len(records)