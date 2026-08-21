from collections.abc import Iterable
from logging import getLogger
from queue import Empty, Full, Queue

from ...functional import Consumer, ContinuationProvider
from ...logic.ranges import InclusiveRange, RangedCounter
from . import QueueReader, QueueWriter

logger = getLogger(__name__)


def create_adaptive_queue_writer[T](
    timeout_seconds_range: InclusiveRange,
    timeout_factor: float,
) -> QueueWriter[T]:
    """
    Higher-order function that, via the given parameters, creates a function for writing items
    to any queue - adapting its speed to the current state of the queue.

    More precisely, the returned function has this signature:

    (Queue[T], ContinuationProvider, Iterable[T]) -> None

    that is, it takes:

    * the target queue

    * a ContinuationProvider - which is a function like () -> Bool (see below)

    * the items to be written to the queue

    The returned function will try to write every item to the queue via a loop that is infinite
    until:

    * all the items have been written to the queue

    * the ContinuationProvider returns False

    * an exception occurs

    Enqueuing an item occurs with a timeout, with an initial value given by the lowest bound
    of the requested range: when the enqueuing fails because the queue is Full, the timeout
    is multiplied by the given factor, otherwise it is divided by the factor - always remaining
    in the range passed to the higher-order function.
    """
    if timeout_factor < 1:
        raise ValueError(timeout_factor)

    timeout_seconds = RangedCounter(
        inclusive_range=timeout_seconds_range,
        initial_value=timeout_seconds_range.lower,
    )

    def writer(
        queue: Queue[T],
        continuation_provider: ContinuationProvider,
        items: Iterable[T],
    ) -> None:
        for item in items:
            if not continuation_provider():
                if __debug__:
                    logger.info("Stopping the queue writer, as requested")
                return

            while True:
                try:
                    queue.put(item, timeout=timeout_seconds.value)
                except Full:
                    if __debug__:
                        logger.debug("The queue is full!")

                    if not continuation_provider():
                        if __debug__:
                            logger.info("Stopping writing to the queue, as requested")
                        return

                    timeout_seconds.value *= timeout_factor
                else:
                    timeout_seconds.value /= timeout_factor
                    break

    return writer


def create_adaptive_queue_reader[T](
    item_consumer: Consumer[T],
    timeout_seconds_range: InclusiveRange,
    timeout_factor: float,
) -> QueueReader[T]:
    """
    Higher-order function that, via the given parameters, creates a function for reading items
    from any queue - adapting its speed to the current state of the queue.

    More precisely, the returned function has this signature:

    (Queue[T], ContinuationProvider) -> None

    that is, it takes:

    * the source queue

    * a ContinuationProvider - which is a function like () -> Bool (see below)


    The returned function will run an infinite loop constantly performing a few steps:

    1. read an item from the queue
    2. process it via the consumer function passed to the higher-order function
    3. notify the queue via its task_done() method


    The above loop only stops as soon as:

    * the ContinuationProvider returns False when the queue is Empty

    * an exception occurs - for example, in the consumer function

    Each iteration of the loop tries to dequeue an item with a timeout having initial value
    given by the lowest bound of the requested range: when the dequeuing fails because the
    queue is Empty, the timeout is multiplied by the given factor, otherwise it is divided
    by the factor - always remaining in the range passed to the higher-order function.
    """
    if timeout_factor < 1:
        raise ValueError(timeout_factor)

    timeout_seconds = RangedCounter(timeout_seconds_range, timeout_seconds_range.lower)

    def reader(queue: Queue[T], continuation_provider: ContinuationProvider) -> None:
        while True:
            try:
                item = queue.get(timeout=timeout_seconds.value)
            except Empty:
                if __debug__:
                    logger.debug("The queue is empty!")

                if not continuation_provider():
                    if __debug__:
                        logger.info("Stopping reading from the queue, as requested")
                    return

                timeout_seconds.value *= timeout_factor
            else:
                timeout_seconds.value /= timeout_factor

                try:
                    item_consumer(item)
                finally:
                    queue.task_done()

    return reader
