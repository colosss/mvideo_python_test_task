from src.core.domain.models import HttpLogRecord
from src.infrastructure.database.models import HttpLogModel

def http_log_db_to_domain(log: HttpLogModel)-> HttpLogRecord:
    return HttpLogRecord(
        ip=log.ip,
        created_at=log.created_at,
        method=log.method,
        uri=log.uri,
        status_code=log.status_code,
        raw_log=log.raw_log,
    )