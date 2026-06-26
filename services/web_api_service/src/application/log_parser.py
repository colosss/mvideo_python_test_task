from ipaddress import ip_address
from src.core.domain.models import ParsedHttpLog

ALLOWED_HTTP_METHOD={
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "HEAD",
    "OPTIONS",
}

class InvalidLogFormatError(ValueError):
    pass

def parse_http_log_line(raw_log: str)->ParsedHttpLog:
    normalized=raw_log.strip()
    parts=normalized.split()

    if len(parts)!=4:
        raise InvalidLogFormatError(
            "Expected format: '{IP address} {HTTP method} {UTI} {HTTP status code}"
        )
    raw_ip, method, uri, raw_status_code=parts

    try:
        parsed_ip=ip_address(raw_ip)
    except ValueError as exc:
        raise InvalidLogFormatError("Invalid IP address") from exc

    method=method.upper()
    if method not in ALLOWED_HTTP_METHOD:
        raise InvalidLogFormatError("Invalid HTTP method")
    
    if not uri.startswith("/") or any(ch.isspace() for ch in uri):
        raise InvalidLogFormatError("Invalid URI")
    
    try:
        status_code=int(raw_status_code)
    except ValueError as exc:
        raise InvalidLogFormatError("HTTP status code must be an integer") from exc
    
    if status_code<100 or status_code>599:
        raise InvalidLogFormatError("HTTP status code must be between 100 and 599")
    
    return ParsedHttpLog(
        ip=str(parsed_ip),
        method=method,
        uri=uri,
        status_code=status_code,
        raw_log=normalized,
    )