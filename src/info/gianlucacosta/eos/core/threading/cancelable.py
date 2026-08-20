from abc import ABC, abstractmethod
from threading import Thread
from typing import Any


class CancelableThread(Thread, ABC):
    """
    Thread subclass that can be canceled by its clients.

    More precisely, the request_cancel() method - accessible to clients - sets an
    internal flag when called.

    It is up to you to implement the run() method in a way that keeps track of
    that flag - which is also accessible via a read-only property.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._never_canceled = True

    def request_cancel(self) -> None:
        """
        Notifies the thread that a cancel request was performed.

        The actual effect only depends on the thread implementation.
        """
        self._never_canceled = False

    @property
    def never_canceled(self) -> bool:
        """
        Returns whether a notification request was already sent to the thread.
        """
        return self._never_canceled

    @abstractmethod
    def run(self) -> None:
        """
        Implement this abstract methods keeping track of the internal flag
        """


class CancelableThreadHandle:
    """
    Minimalist proxy to a CancelableThread.

    In particular, it just contains the request_cancel() and join() methods, that simply proxy the
    ones in CancelableThread.

    A very interesting patterns consists in creating and starting a CancelableThread within a
    function, then returning a CancelableThreadHandle to it, so that the client can only access
    a minimalist operational surface.
    """

    def __init__(self, thread: CancelableThread) -> None:
        self._thread = thread

    def request_cancel(self) -> None:
        self._thread.request_cancel()

    def join(self, timeout: float | None = None) -> None:
        self._thread.join(timeout)
