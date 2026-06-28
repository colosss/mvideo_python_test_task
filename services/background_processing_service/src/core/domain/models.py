from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class RemoteHttpLogRecord:
    id: str
    created: str
    log: dict[str, Any]

@dataclass(frozen=True)
class ExportState:
    last_created: str|None=None