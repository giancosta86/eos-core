from pytest import mark, raises

from .retries import call_with_retries


class RetryTestException(Exception):
    pass


class TestRunWithRetries:
    @mark.parametrize(["max_attempts", "timeout_seconds"], [[0, 4], [-1, 4], [3, -6]])
    def test_when_wrong_arguments(self, max_attempts, timeout_seconds):
        with raises(ValueError):
            call_with_retries(
                lambda: None,
                max_attempts=max_attempts,
                timeout_seconds=timeout_seconds,
            )

    def test_when_no_exceptions(self):
        counter = 0

        def increment_counter():
            nonlocal counter
            counter += 1

        call_with_retries(increment_counter, max_attempts=3, timeout_seconds=0.1)

        assert counter == 1

    def test_with_exception_but_succeeding(self):
        counter = 0

        def increment_counter():
            nonlocal counter
            counter += 1

            if counter < 2:
                raise RetryTestException()

        call_with_retries(increment_counter, max_attempts=3, timeout_seconds=0.1)

        assert counter == 2

    def test_with_exception_and_failing(self):
        counter = 0

        def increment_counter():
            nonlocal counter
            counter += 1

            if counter <= 3:
                raise RetryTestException()

        with raises(RetryTestException):
            call_with_retries(increment_counter, max_attempts=3, timeout_seconds=0.1)

        assert counter == 3

    def test_with_int_provider(self):
        result = call_with_retries(lambda: 90, max_attempts=3, timeout_seconds=0)

        assert result == 90

    def test_with_initially_failing_int_provider(self):
        provider_call_count = 0

        def int_provider():
            nonlocal provider_call_count
            provider_call_count += 1

            if provider_call_count == 3:
                return 90

            raise RetryTestException()

        result = call_with_retries(int_provider, max_attempts=3, timeout_seconds=0)
        assert result == 90
