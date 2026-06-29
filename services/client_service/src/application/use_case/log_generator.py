import random
import threading

from src.application.log_generator import RandomHttpLogGenerator
from src.application.ports import LogSender, SentLogLogger

class GenerateAndSendLogUseCase:
    def __init__(
        self,
        *,
        generator: RandomHttpLogGenerator,
        sender: LogSender,
        sent_log_logger: SentLogLogger,
        max_delay_ms: int,
    )->None:
        self._generator=generator
        self._sender=sender
        self._sent_log_logger=sent_log_logger
        self._max_delay_ms=max_delay_ms
        self._random=random.Random()

    def execute(
        self,
        *,
        worker_id: int,
        stop_event: threading.Event,
        requests_limit: int,
    )->None:
        sent_count=0
        while not stop_event.is_set():
            if requests_limit and sent_count>=requests_limit:
                return
            
            delay=self._random.uniform(0, self._max_delay_ms)/1000
            if delay and stop_event.wait(delay):
                return
            
            generated_log=self._generator.generate()
            result=self._sender.send(generated_log.line)
            self._sent_log_logger.log_attempt(
                worker_id=worker_id,
                log=generated_log,
                result=result,
            )
            sent_count+=1