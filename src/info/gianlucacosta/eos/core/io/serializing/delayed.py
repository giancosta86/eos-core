from abc import ABC, abstractmethod
from logging import getLogger
from typing import Any, Self

from ...functional import Mapper


class DelayedSerializer[T](ABC):
    """
    Abstract class ensuring that it will eventually serialize objects of the given type
    once its flush() methods gets called:

    * directly, by the client

    * at the end of a "with" block

    Clients can request serialization - which is only guaranteed upon flush() - by calling
    the request_serialize() method.

    Apart from the context manager and the abstract methods, no implementation detail
    is provided by this class.
    """

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.flush()

    @abstractmethod
    def request_serialize(self, item: T) -> None:
        pass

    @abstractmethod
    def flush(self) -> None:
        pass


class MappingBufferedSerializer[T, TBufferedItem](DelayedSerializer[T]):
    """
    Delayed serializer that, upon a serialization request:

    1. stores into its internal buffer the result of its mapper applied to the given item

    2. automatically performs flush() once its internal buffer exceeds the given size
    """

    def __init__(
        self, item_mapper: Mapper[T, TBufferedItem], max_buffer_len: int
    ) -> None:
        self._mapper = item_mapper
        self._max_buffer_len = max_buffer_len
        self._buffer: list[TBufferedItem] = []

        self._logger = getLogger(type(self).__name__)

    def request_serialize(self, item: T) -> None:
        buffered_item = self._mapper(item)
        self._buffer.append(buffered_item)

        if len(self._buffer) == self._max_buffer_len:
            if __debug__:
                self._logger.info("The buffer is full! Now flushing...")
            self.flush()

    def flush(self) -> None:
        self._buffer = []


class CompositeDelayedSerializer[T](DelayedSerializer[Any]):
    """
    Delayed serializer that can serialize any object - actually delegating the serialization
    process to its internal serializers.

    More precisely, upon a serialization request, it detects the type of the object to be
    serialized and calls the internal serializer registered for that type.

    Registration can be performed via the add_serializer() method.

    Last but not least, the flush() method ensures that all the internal serializers are
    flushed as well: any exception is ignored, but logged if in __debug__.
    """

    def __init__(self) -> None:
        self._serializers_by_type: dict[Any, DelayedSerializer[Any]] = {}
        self._logger = getLogger(type(self).__name__)

    def request_serialize(self, item: Any) -> None:
        """
        Delegates the serialization of the given object to one of the internal serializers.
        """
        serializer = self._serializers_by_type[type(item)]
        serializer.request_serialize(item)

    def flush(self) -> None:
        """
        Flushes all the internal serializers.

        Any exception is caught and logged if in __debug__.
        """
        for serializer in self._serializers_by_type.values():
            try:
                serializer.flush()
            except Exception as ex:  # noqa: BLE001
                self._logger.error(
                    "Error while flushing %s: %r",
                    type(serializer).__name__,
                    ex,
                )

    def add_serializer(
        self, item_type: type[T], serializer: DelayedSerializer[T]
    ) -> None:
        """
        Registers an internal serializer for the given type.

        There can be at most one internal serializer per type.
        """
        if item_type in self._serializers_by_type:
            raise KeyError("Type already registered")

        self._serializers_by_type[item_type] = serializer
