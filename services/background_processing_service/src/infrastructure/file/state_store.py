import json
from pathlib import Path

from src.application.ports import ExportStateStore
from src.core.domain.models import ExportState

class JsonExportStateStore(ExportStateStore):
    def __init__(self, path: str)->None:
        self._path=Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def load(self)->ExportState:
        if not self._path.exists():
            return ExportState()

        with self._path.open("r", encoding="utf-8") as file:
            payload=json.load(file)

        return ExportState(last_created=payload.get("last_created"))
    
    def save(self, state: ExportState)->None:
        tmp_path=self._path.with_suffix(self._path.suffix+".tmp")
        with tmp_path.open("w", encoding="utf-8") as file:
            json.dump({"last_created": state.last_created}, file, ensure_ascii=False)
        tmp_path.replace(self._path)