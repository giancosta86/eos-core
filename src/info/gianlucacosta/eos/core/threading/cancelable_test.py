from collections.abc import Callable

from .cancelable import CancelableThread, CancelableThreadHandle


class CancelableTestThread(CancelableThread):
    def __init__(self, loop_body: Callable[[CancelableThread], bool]) -> None:
        super().__init__()
        self._loop_body = loop_body

    def run(self) -> None:
        while self._never_canceled:
            if not self._loop_body(self):
                break


def test_never_canceling():
    counter = 0

    def body(_: CancelableThread):
        nonlocal counter
        counter += 1

        return counter < 50

    thread = CancelableTestThread(body)
    thread.start()
    thread.join()

    assert counter == 50
    assert thread.never_canceled


def test_canceling_via_self():
    counter = 0

    def body(thread: CancelableThread):
        nonlocal counter
        counter += 1

        if counter == 50:
            thread.request_cancel()

        return True

    thread = CancelableTestThread(body)
    thread.start()
    thread.join()

    assert counter == 50
    assert not thread.never_canceled


def test_canceling_via_handle() -> None:
    counter = 0

    thread_handle: CancelableThreadHandle | None = None

    def body(_: CancelableThread):
        nonlocal counter
        counter += 1

        if counter == 50 and thread_handle:
            thread_handle.request_cancel()

        return True

    thread = CancelableTestThread(body)
    thread_handle = CancelableThreadHandle(thread)
    thread.start()
    thread_handle.join()

    assert counter == 50
    assert not thread.never_canceled
