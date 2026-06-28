import fcntl
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from src.application.ports import ExportLock

class FcntlExportLock(ExportLock):
    def __int__(self, path: str)->None:
        self._path=Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def acquire(self)->Iterator[None]:
        with self._path.open("a+", encoding="utf-8") as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                