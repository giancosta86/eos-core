from .safe import SafeThread


class MyTestException(Exception):
    def __init__(self, alpha: int, beta: int) -> None:
        super().__init__()
        self.alpha = alpha
        self.beta = beta


class TestSafeThread:
    def test_without_exceptions(self):
        class MyThread(SafeThread):
            def _safe_run(self) -> None:
                pass

        my_thread = MyThread()
        my_thread.start()
        my_thread.join()

        assert my_thread.exception is None

    def test_with_exception(self):
        class MyThread(SafeThread):
            def _safe_run(self) -> None:
                raise MyTestException(alpha=7, beta=92)

        my_thread = MyThread()
        my_thread.start()
        my_thread.join()

        match my_thread.exception:
            case MyTestException() as ex:
                assert ex.alpha == 7
                assert ex.beta == 92

            case _:
                assert False
