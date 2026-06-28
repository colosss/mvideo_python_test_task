from abc import ABC, abstractmethod

from src.core.domain.models import GeneratedHttpLog, SendResult

class LogSender(ABC):
    @abstractmethod
    def send(self, log_line: str)->SendResult: ...

class SentLogLogger(ABC):
    @abstractmethod
    def log_attempt(
        self,
        *,
        worker_id: int,
        log: GeneratedHttpLog,
        result: SendResult,
    )->None: ...