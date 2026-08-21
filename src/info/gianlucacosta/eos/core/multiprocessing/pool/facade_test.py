from collections.abc import Callable
from time import sleep

from pytest import raises

from ...threading.atomic import Atomic
from . import InThreadPool
from .facade import ProcessPoolFacade


def special_sum(alpha: int, beta: int) -> int:
    sleep(0.05)
    return alpha + beta + 1


def special_sum_with_error(alpha: int, beta: int) -> int:
    if alpha == 90:
        return 90 // 0

    sleep(0.05)
    return alpha + beta + 1


class MyProcessPoolFacade(ProcessPoolFacade[int]):
    def __init__(
        self,
        worker_function: Callable[..., int],
        atomic: Atomic[int],
        max_pending_async_requests: int,
    ):
        super().__init__(
            pool_factory=InThreadPool,
            worker_function=worker_function,
            max_pending_async_requests=max_pending_async_requests,
        )
        self._atomic = atomic
        self._error_counter = Atomic(0)

    def _on_worker_result(self, worker_result: int) -> None:
        self._atomic.map(lambda value: value + worker_result)

    def _on_worker_error(self, _: BaseException) -> None:
        self._error_counter.map(lambda value: value + 1)

    def send_numbers(self, alpha: int, beta: int) -> None:
        self._send_to_worker(alpha, beta)

    @property
    def error_counter(self) -> int:
        return self._error_counter.get()


class TestProcessPoolFacade:
    def test_with_common_scenario(self):
        atomic = Atomic(0)
        with MyProcessPoolFacade(
            special_sum, atomic, max_pending_async_requests=2
        ) as pool_facade:
            pool_facade.send_numbers(9, 4)
            pool_facade.send_numbers(3, 8)
            pool_facade.send_numbers(5, 7)
            pool_facade.send_numbers(3, 2)
            pool_facade.send_numbers(14, 7)

        assert atomic.get() == (9 + 4) + (3 + 8) + (5 + 7) + (3 + 2) + (14 + 7) + 1 * 5
        assert pool_facade.error_counter == 0

    def test_with_exceptions(self):
        atomic = Atomic(0)
        with MyProcessPoolFacade(
            special_sum_with_error, atomic, max_pending_async_requests=2
        ) as pool_facade:
            pool_facade.send_numbers(9, 4)
            pool_facade.send_numbers(90, 8)
            pool_facade.send_numbers(5, 7)
            pool_facade.send_numbers(90, 2)
            pool_facade.send_numbers(14, 7)

        assert atomic.get() == (9 + 4) + (5 + 7) + (14 + 7) + 1 * 3
        assert pool_facade.error_counter == 2

    def test_with_negative_async_requests(self):
        atomic = Atomic(0)

        with raises(ValueError) as ex:
            MyProcessPoolFacade(
                special_sum_with_error, atomic, max_pending_async_requests=-5
            )

        assert ex.value.args == (-5,)
