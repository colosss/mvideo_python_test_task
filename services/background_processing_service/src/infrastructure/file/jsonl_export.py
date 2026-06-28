import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from src.application.ports import ExportWriter
from src.core.domain.models import RemoteHttpLogRecord

class JsonlExportWriter(ExportWriter):
    def __init__(self, path: str)->None:
        self._path=Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, records: Sequence[RemoteHttpLogRecord])->None:
        exported_at=datetime.now(timezone.utc).isoformat()
        with self._path.open("a", encoding="utf-8") as file:
            for record in records:
                payload={
                    "exported_at": exported_at,
                    "record": asdict(record),
                }
                file.write(json.dumps(payload, ensure_ascii=False)+"\n")