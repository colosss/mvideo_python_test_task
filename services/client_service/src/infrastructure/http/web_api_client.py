import httpx

from src.application.ports import LogSender
from src.core.domain.models import SendResult

class HttpxWebApiLogSender(LogSender):
    def __init__(self, base_url: str, timeout_seconds: float)->None:
        self._base_url=base_url.rstrip("/")
        self._client=httpx.Client(timeout=timeout_seconds)

    def send(self, log_line:str)->SendResult:
        try:
            response=self._client.post(
                f"{self._base_url}/api/data",
                json={"log": log_line},
            )
        except httpx.HttpError as exc:
            return SendResult(ok=False, error=str(exc))
        
        if 200<=response.status_code<300:
            return SendResult(ok=True, status_code=response.status_code)
        
        return SendResult(
            ok=False,
            status_code=response.status_code,
            error=response.text[:500],
        )
    
    def close(self)->None:
        self._client.close()