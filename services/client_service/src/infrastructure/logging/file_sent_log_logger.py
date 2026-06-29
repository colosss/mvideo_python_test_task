import json
import threading
from datetime import datetime, timezone
from pathlib import Path

from src.application.ports import SentLogLogger
from src.core.domain.models import GeneratedHttpLog, SendResult

class JsonSentLogLogger(SentLogLogger):
    def __init__(self, path: str)-> None:
        self._path=Path(path)
        self._lock=threading.Lock()
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def log_attempt(
        self, 
        *, 
        worker_id: int, 
        log: GeneratedHttpLog, 
        result: SendResult,
        )->None:
        payload={
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "worker_id": worker_id,
            "log": log.line,
            "ok": result.ok,
            "status_code": result.status_code,
            "error": result.error,
        }
        line=json.dumps(payload, ensure_ascii=False)
        with self._lock:
            with self._path.open("a", encoding="utf-8") as file:
                file.write(line+"\n")