from typing import Any, Sequence

import httpx

from src.application.ports import RemoteLogReader
from src.core.domain.models import RemoteHttpLogRecord

class HttpxWebApiLogReader(RemoteLogReader):
    def __init__(self, base_url: str, timeout_seconds: float)->None:
        self._base_url=base_url.rstrip("/")
        self._client=httpx.Client(timeout=timeout_seconds)

    def fetch_logs(
        self, 
        *, 
        created_after:str|None, 
        limit: int,
    )->Sequence{RemoteHttpLogRecord}:
        params:dict[str, Any]={"limit": limit, "order": "asc"}
        if created_after:
            params["created_after"]=created_after

        response=self._client.get(f"{self._base_url}/api/data", params=params)
        response.raise_for_status()
        payload=response.json()

        return [
            RemoteHttpLogRecord(
                id=item["id"],
                created=item["created"],
                log=item["log"],
            )
            for item in payload
        ]
    
    def close(self)->None:
        self._client.close()