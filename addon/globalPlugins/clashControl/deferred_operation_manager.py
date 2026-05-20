import threading
import time

try:
    from logHandler import log as logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


class DeferredOperationManager:
    def __init__(self):
        self._operations: dict[str, int] = {}

    def get_current_operation_id(self, operation_key: str) -> int:
        return self._operations[operation_key]

    def get_next_operation_id(self, operation_key: str) -> int:
        current = self._operations.setdefault(operation_key, 0)
        self._operations[operation_key] = current + 1
        return current + 1

    def schedule(self, operation_key: str, delay: int, callback, *args, **kwargs):
        threading.Thread(
            target=self._run_operation,
            args=(
                self.get_next_operation_id(operation_key),
                operation_key,
                delay,
                callback,
                args,
                kwargs,
            ),
        ).start()

    def _run_operation(
        self,
        initial_operation_id: int,
        operation_key: str,
        delay: int,
        callback,
        args,
        kwargs,
    ):
        time.sleep(delay)
        current_operation_id = self.get_current_operation_id(operation_key)
        if current_operation_id != initial_operation_id:
            return
        try:
            callback(*args, **kwargs)
        except Exception:
            logger.exception(f"Failed to execute operation {operation_key}")
