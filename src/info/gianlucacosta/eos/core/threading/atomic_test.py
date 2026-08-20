from functools import wraps
from threading import Thread

from ..functional import Consumer, Producer
from .atomic import Atomic


class TestAtomicWithOneThread:
    def test_set(self):
        atomic = Atomic(9)
        atomic.set(92)
        assert atomic.get() == 92

    def test_get_then_set(self):
        atomic = Atomic(9)
        assert atomic.get_then_set(90) == 9
        assert atomic.get() == 90

    def test_get_then_map(self):
        atomic = Atomic(5)
        assert atomic.get_then_map(lambda value: value + 90) == 5

    def test_map_then_get(self):
        atomic = Atomic(7)
        assert atomic.map_then_get(lambda value: value + 90) == 97

    def test_map(self):
        atomic = Atomic(90)
        atomic.map(lambda value: value + 1)
        assert atomic.get() == 91


ExpectedResult = int


def multithread_test(expected_final_value: ExpectedResult, thread_count: int = 5):
    def decorator(test_function: Producer[Consumer[Atomic[int]]]):
        @wraps(test_function)
        def wrapper():
            counter = Atomic(0)

            atomic_consumer = test_function()

            threads = [
                Thread(target=lambda: atomic_consumer(counter))
                for _ in range(thread_count)
            ]

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            assert counter.get() == expected_final_value

        return wrapper

    return decorator


@multithread_test(900, thread_count=2)
def test_get_then_map():
    def body(atomic: Atomic[int]):
        for _ in range(450):
            atomic.get_then_map(lambda value: value + 1)

    return body


@multithread_test(900, thread_count=2)
def test_map_then_get():
    def body(atomic: Atomic[int]):
        for _ in range(450):
            atomic.map_then_get(lambda value: value + 1)

    return body
