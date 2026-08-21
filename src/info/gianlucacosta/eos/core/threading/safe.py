from abc import ABC, abstractmethod
from logging import getLogger
from threading import Thread
from typing import Any


class SafeThread(Thread, ABC):
    """
    Thread that will never fail silently because of an exception.

    You just need to implement the abstract _safe_run() method:

    * if the method ends without exceptions, nothing happens

    * otherwise, should any uncaught exception lead to the end of the method, it is logged and
      also stored into the "exception" property of this thread object, for later inspection

    A logger is also provided (in the _logger field), that automatically logs entering/exiting,
    as well as unhandled exceptions.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._exception: Exception | None = None
        self._logger = getLogger(type(self).__name__)

    @property
    def exception(self) -> Exception | None:
        return self._exception

    def run(self) -> None:
        try:
            if __debug__:
                self._logger.info("Just entered %s!", type(self).__name__)

            self._safe_run()
        except Exception as ex:  # noqa: BLE001
            self._exception = ex

            self._logger.error("Unhandled exception in %s: %r", type(self).__name__, ex)
        finally:
            if __debug__:
                self._logger.info("Now exiting %s!", type(self).__name__)

    @abstractmethod
    def _safe_run(self) -> None:
        """
        Implement this method, without worrying for unhandled exceptions as well as
        entering/exiting log messages
        """
