from dataclasses import dataclass

@dataclass(frozen=True)
class GeneratedHttpLog:
    ip: str
    method: str
    uri: str
    status_code: int

    @property
    def line(self)->str:
        return f"{self.ip} {self.method} {self.uri} {self.status_code}"
    

@dataclass(frozen=True)
class SendResult:
    ok: bool
    status_code: int|None=None
    error: str|None=None