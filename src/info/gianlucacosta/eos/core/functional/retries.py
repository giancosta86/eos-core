from logging import getLogger
from time import sleep

from . import Producer

logger = getLogger(__name__)


def call_with_retries[T](producer: Producer[T], max_attempts: int, timeout_seconds: float) -> T:
    """
    Tries to call the given producer at most "max_attempts" times, with a timeout in seconds
    before each retry; the execution ends as soon as the producer ends without exceptions,
    thus providing the return value of this function, or when all the attempts fail.

    * "max_attempts" must be >= 1
    * "timeout_seconds" must be >= 0

    Exceptions are ignored - but logged in __debug__ - until the last retry, when they bubble out
    of the function.
    """
    if max_attempts <= 0:
        raise ValueError(max_attempts)

    if timeout_seconds < 0:
        raise ValueError(timeout_seconds)

    attempts_done = 0

    while True:
        try:
            return producer()
        except Exception as ex:
            attempts_done += 1

            if attempts_done == max_attempts:
                raise

            if __debug__:
                logger.warning(ex)

            sleep(timeout_seconds)
