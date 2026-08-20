from collections.abc import Iterable
from functools import wraps
from queue import Queue
from threading import Thread
from time import sleep

from pytest import raises

from ...functional import AnyCallable
from ...logic.ranges import InclusiveRange
from ..queues_test import (
    FAST_AGENT_CONFIGURATION,
    SLOW_AGENT_CONFIGURATION,
    AgentConfigurationForTesting,
)
from . import QueueWriter
from .adaptive import create_adaptive_queue_reader, create_adaptive_queue_writer


def agent_scenario(
    writer_configuration: AgentConfigurationForTesting,
    reader_configuration: AgentConfigurationForTesting,
    queue_max_size: int,
    source: list[int],
):
    def decorator(test_function: AnyCallable) -> AnyCallable:
        @wraps(test_function)
        def wrapper() -> None:
            result: list[int] = []

            queue = Queue[int](maxsize=queue_max_size)

            def item_producer() -> Iterable[int]:
                for item in source:
                    sleep(writer_configuration.operation_sleep_seconds)
                    yield item

            write_items_to_queue: QueueWriter[int] = create_adaptive_queue_writer(
                timeout_seconds_range=writer_configuration.timeout_seconds_range,
                timeout_factor=writer_configuration.timeout_factor,
            )

            def write_to_result(item: int) -> None:
                result.append(item)
                sleep(reader_configuration.operation_sleep_seconds)

            read_items_from_queue = create_adaptive_queue_reader(
                item_consumer=write_to_result,
                timeout_seconds_range=reader_configuration.timeout_seconds_range,
                timeout_factor=reader_configuration.timeout_factor,
            )

            writing_thread = Thread(
                target=lambda: write_items_to_queue(
                    queue, lambda: True, item_producer()
                )
            )
            reading_thread = Thread(
                target=lambda: read_items_from_queue(
                    queue, lambda: len(result) < len(source)
                )
            )

            writing_thread.start()
            reading_thread.start()

            writing_thread.join()
            reading_thread.join()

            assert result == source

        return wrapper

    return decorator


@agent_scenario(
    writer_configuration=FAST_AGENT_CONFIGURATION,
    reader_configuration=FAST_AGENT_CONFIGURATION,
    queue_max_size=2,
    source=list(range(5)),
)
def test_fast_writer_and_fast_reader():
    pass


@agent_scenario(
    writer_configuration=SLOW_AGENT_CONFIGURATION,
    reader_configuration=FAST_AGENT_CONFIGURATION,
    queue_max_size=1,
    source=list(range(4)),
)
def test_slow_writer_and_fast_reader():
    pass


@agent_scenario(
    writer_configuration=FAST_AGENT_CONFIGURATION,
    reader_configuration=SLOW_AGENT_CONFIGURATION,
    queue_max_size=1,
    source=list(range(4)),
)
def test_fast_writer_and_slow_reader():
    pass


def test_create_writer_with_zero_point_nine_timeout_factor():
    with raises(ValueError) as ex:
        create_adaptive_queue_writer(InclusiveRange(7, 90), timeout_factor=0.9)

    assert ex.value.args == (0.9,)


def test_create_writer_with_negative_timeout_factor():
    with raises(ValueError) as ex:
        create_adaptive_queue_writer(InclusiveRange(7, 90), timeout_factor=-7)

    assert ex.value.args == (-7,)


def test_create_reader_with_zero_point_nine_timeout_factor():
    with raises(ValueError) as ex:
        create_adaptive_queue_reader(
            lambda _: None, InclusiveRange(7, 90), timeout_factor=0.9
        )

    assert ex.value.args == (0.9,)


def test_create_reader_with_negative_timeout_factor():
    with raises(ValueError) as ex:
        create_adaptive_queue_reader(
            lambda _: None, InclusiveRange(7, 90), timeout_factor=-9
        )

    assert ex.value.args == (-9,)


def test_interrupted_writer() -> None:
    result: list[int] = []

    queue = Queue[int](maxsize=3)

    def item_producer() -> Iterable[int]:
        for item in range(90):
            sleep(FAST_AGENT_CONFIGURATION.operation_sleep_seconds)
            yield item

    write_items_to_queue: QueueWriter[int] = create_adaptive_queue_writer(
        timeout_seconds_range=FAST_AGENT_CONFIGURATION.timeout_seconds_range,
        timeout_factor=FAST_AGENT_CONFIGURATION.timeout_factor,
    )

    last_expected_item = 7
    canceled = False

    def write_to_result(item: int) -> None:
        nonlocal canceled

        if not canceled:
            result.append(item)

        if item == last_expected_item:
            canceled = True

        sleep(FAST_AGENT_CONFIGURATION.operation_sleep_seconds)

    read_items_from_queue = create_adaptive_queue_reader(
        item_consumer=write_to_result,
        timeout_seconds_range=FAST_AGENT_CONFIGURATION.timeout_seconds_range,
        timeout_factor=FAST_AGENT_CONFIGURATION.timeout_factor,
    )

    writing_thread = Thread(
        target=lambda: write_items_to_queue(
            queue, lambda: not canceled, item_producer()
        )
    )
    reading_thread = Thread(
        target=lambda: read_items_from_queue(queue, lambda: not canceled)
    )

    writing_thread.start()
    reading_thread.start()

    writing_thread.join()
    reading_thread.join()

    expected_list = list(range(last_expected_item + 1))

    print("🤔RESULT IS: " + str(result))
    print("🎯EXPECTED LIST IS: " + str(expected_list))
    assert result == expected_list


def test_interrupted_writer_without_reader():
    source = range(90)

    queue = Queue[int](maxsize=1)

    def item_producer() -> Iterable[int]:
        for item in source:
            sleep(FAST_AGENT_CONFIGURATION.operation_sleep_seconds)
            yield item

    write_items_to_queue: QueueWriter[int] = create_adaptive_queue_writer(
        timeout_seconds_range=FAST_AGENT_CONFIGURATION.timeout_seconds_range,
        timeout_factor=FAST_AGENT_CONFIGURATION.timeout_factor,
    )

    max_continuation_call_count = 5
    continuation_call_count = 0

    def can_continue() -> bool:
        nonlocal continuation_call_count
        continuation_call_count += 1

        return continuation_call_count < max_continuation_call_count

    writing_thread = Thread(
        target=lambda: write_items_to_queue(queue, can_continue, item_producer())
    )
    writing_thread.start()

    writing_thread.join()
