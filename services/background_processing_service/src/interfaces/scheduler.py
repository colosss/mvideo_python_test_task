import logging
import signal
import threading

from src.application.use_cases import FetchAndPersistLogsUseCase
from src.config.settings import Settings
from src.infrastructure.file.file_lock import FcntlExportLock
from src.infrastructure.file.jsonl_export import JsonlExportWriter
from src.infrastructure.file.state_store import JsonExportStateStore
from src.infrastructure.http.web_api_client import HttpxWebApiLogReader

logger=logging.getLogger(__name__)

def _install_signal_handlers(stop_event: threading.Event)->None:
    def handler(signum: int, frame: object)->None:
        logger.info("Received signal %s, stopping background service", signum)
        stop_event.set()

    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)

def run_background_service(settings: Settings)->None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    stop_event=threading.Event()
    _install_signal_handlers(stop_event)

    reader=HttpxWebApiLogReader(
        settings.WEB_API_BASE_URL,
        settings.BACKGROUND_HTTP_TIMEOUT_SECONDS,
    )
    use_case=FetchAndPersistLogsUseCase(
        reader=reader,
        writer=JsonlExportWriter(settings.EXPORT_FILE_PATH),
        state_store=JsonExportStateStore(settings.EXPORT_STATE_PATH),
        export_lock=FcntlExportLock(settings.EXPORT_LOCK_PATH),
        batch_limit=settings.EXPORT_BATCH_LIMIT,
    )

    logger.info(
        "Background exporter started: interval=%ss file=%s",
        settings.FETCH_INTERVAL_SECONDS,
        settings.EXPORT_FILE_PATH,
    )
    try:
        while not stop_event.is_set():
            try:
                exported_count=use_case.execute()
                logger.info("Exported %s log records", exported_count)
            except Exception:
                logger.exception("Background export iteration failed")

            stop_event.wait(settings.FETCH_INTERVAL_SECOND)

    finally:
        reader.close()
        logger.info("Background service stopped")