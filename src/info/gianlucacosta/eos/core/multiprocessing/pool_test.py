from operator import add

from pytest import raises

from .pool import InThreadPool


def my_diff(x: int, y: int):
    return x - y


class PoolTestException(Exception):
    pass


def failing():
    raise PoolTestException()


class TestInProcessPool:
    def test_apply(self):
        pool = InThreadPool()
        result = pool.apply(my_diff, [98], {"y": 6})

        assert result == 92

    def test_apply_with_error(self):
        pool = InThreadPool()

        with raises(PoolTestException):
            pool.apply(failing)

    def test_apply_async_without_errors(self):
        def callback(value: int):
            assert value == 98

        pool = InThreadPool()
        pool.apply_async(my_diff, [102], {"y": 4}, callback=callback)

    def test_apply_async_with_errors_with_error_callback(self):
        def callback(_: int):
            assert False

        exception_caught = False

        def error_callback(exception: Exception):
            nonlocal exception_caught
            exception_caught = isinstance(exception, PoolTestException)

        pool = InThreadPool()
        pool.apply_async(failing, callback=callback, error_callback=error_callback)
        assert exception_caught

    def test_apply_async_with_errors_without_error_callback(self):
        def callback(_: int):
            assert False

        pool = InThreadPool()

        with raises(PoolTestException):
            pool.apply_async(failing, callback=callback, error_callback=None)

    def test_enter_and_exit(self):
        with InThreadPool() as pool:
            result = pool.apply(add, [8, 90])

            assert result == 98

    def test_close(self):
        InThreadPool().close()

    def test_terminate(self):
        InThreadPool().terminate()

    def test_join(self):
        InThreadPool().join()
