import logging
import random
import signal
import threading
from collections.abc import Callable

from src.application.log_generator import RandomHttpLogGenerator
from src.application.use_case.log_generator import GenerateAndSendLogUseCase
from src.config.settings import Settings
from src.infrastructure.http.web_api_client import HttpxWebApiLogSender
from src.infrastructure.logging.file_sent_log_logger import JsonSentLogLogger

logger=logging.getLogger(__name__)

def _install_signal_handlers(stop_event: threading.Event)->None:
    def handler(signum: int, frame: object)-> None:
        logger.info("Received signal %s, stopping client workers", signum)
        stop_event.set()

    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)

def run_client_service(settings: Settings)->None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    stop_event=threading.Event()
    _install_signal_handlers(stop_event)
    sent_log_logger=JsonSentLogLogger(settings.CLIENT_LOG_FILE)

    def make_thread(worker_id: int)->threading.Thread:
        def target()->None:
            sender=HttpxWebApiLogSender(
                settings.WEB_API_BASE_URL,
                settings.CLIENT_HTTP_TIMEOUT_SECONDS,
            )
            try:
                use_case=GenerateAndSendLogUseCase(
                    generator=RandomHttpLogGenerator(random.Random()),
                    sender=sender,
                    sent_log_logger=sent_log_logger,
                    max_delay_ms=settings.CLIENT_MAX_DELAY_MS,
                )
                use_case.execute(
                    worker_id=worker_id,
                    stop_event=stop_event,
                    requests_limit=settings.CLIENT_REQUESTS_PER_WORKER,
                )
            finally:
                sender.close()
        return threading.Thread(target=target, name=f"log-sender-{worker_id}")

    threads=[make_thread(worker_id) for worker_id in range(settings.CLIENT_WORKERS)]

    logger.info(
        "Starting %s workers, max delay %sms, log file %s",
        settings.CLIENT_WORKERS,
        settings.CLIENT_MAX_DELAY_MS,
        settings.CLIENT_LOG_FILE,
    )
    for thread in threads:
        thread.start()

    try:
        while any(thread.is_alive() for thread in threads):
            for thread in threads:
                thread.join(timeout=0.5)

    finally:
        stop_event.set()
        for thread in threads:
            thread.join(timeout=5)
        logger.info("Client service stopped")