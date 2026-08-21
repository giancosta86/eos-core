from abc import ABC, abstractmethod
from collections.abc import Callable
from logging import getLogger
from multiprocessing import cpu_count
from threading import Semaphore
from typing import Any, Self

from . import ProcessPoolFactory


class ProcessPoolFacade[T](ABC):
    """
    Facade to simplify and regulate the usage of a process pool.

    Provides several related benefits:

    * queuing async requests to the pool is not unbounded: trying to exceed such quota
      would block the calling thread until a process in the pool has ended its current task

    * a _send_to_worker() method, to be called by subclasses to actually send requests to the pool

    * an _on_worker_result() abstract method, that must be implemented by subclasses
      to handle the async result of a worker process

    * an optional _on_worker_error() - by default empty, as the infrastructure already provides
      logging - that you can override for custom handling of process errors

    * automatic logging upon error - and, in __debug__, at different points -
      via a _logger field

    * a close_and_join() method, to simplify and log the termination steps

    * __enter__ and __exit__ methods - ensuring that close_and_join() is called at the end
      of a "with" block - instead of the default terminate() call provided by Python's pools
    """

    def __init__(
        self,
        pool_factory: ProcessPoolFactory,
        worker_function: Callable[..., T],
        max_pending_async_requests: int | None = None,
    ):
        """
        Creates the facade - as well as the underlying pool, via the given pool_factory.

        The worker function can be any callable compatible with Pool's apply_async() method.

        The max_pending_async_requests tells how many async requests can be pending at any time -
        defaulting to the number of CPUs in the system.
        """
        if max_pending_async_requests and max_pending_async_requests < 0:
            raise ValueError(max_pending_async_requests)

        self._pool = pool_factory()
        self._worker_function = worker_function
        self._request_semaphore = Semaphore(max_pending_async_requests or cpu_count())
        self._logger = getLogger(type(self).__name__)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close_and_join()

    def close_and_join(self) -> None:
        """
        Closes the pool and joins it - logging every step
        """
        if __debug__:
            self._logger.info("Shutting down the process pool...")

        self._pool.close()

        if __debug__:
            self._logger.info("Process pool closed!")

        self._pool.join()

        if __debug__:
            self._logger.info("Process pool stopped!")

    def _send_to_worker(self, *args: Any, **kwargs: Any) -> None:
        if __debug__:
            self._logger.debug("Trying to get access to a worker process...")

        self._request_semaphore.acquire()

        if __debug__:
            self._logger.debug("Worker process available!")

        self._pool.apply_async(
            self._worker_function,
            args=args,
            kwds=kwargs,
            callback=self._process_worker_result,
            error_callback=self._process_worker_error,
        )

        if __debug__:
            self._logger.debug("Request sent to the worker process!")

    def _process_worker_result(self, worker_result: T) -> None:
        self._request_semaphore.release()

        if __debug__:
            self._logger.debug("Got a result from a worker process!")

        self._on_worker_result(worker_result)

    @abstractmethod
    def _on_worker_result(self, worker_result: T) -> None:
        pass

    def _process_worker_error(self, exception: BaseException) -> None:
        try:
            self._logger.error("Unhandled exception from a worker process: %r", exception)

            self._on_worker_error(exception)
        finally:
            self._request_semaphore.release()

    def _on_worker_error(self, exception: BaseException) -> None:
        pass
