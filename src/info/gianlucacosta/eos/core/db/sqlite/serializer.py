from collections.abc import Callable
from contextlib import closing
from typing import Any

from ...db.sqlite import ConnectionLender
from ...functional import Mapper
from ...io.serializing.delayed import (
    CompositeDelayedSerializer,
    DelayedSerializer,
    MappingBufferedSerializer,
)
from ...reflection import get_single_parameter

type DbRow = list[Any]
type ItemToDbRowMapper[T] = Mapper[T, DbRow]


class ItemToRowSerializer[T](MappingBufferedSerializer[T, DbRow]):
    """
    Buffered serializer that maps an object to a db row - a tuple - via the given mapper.

    Upon flush(), it borrows a connection from the given ConnectionLender and inserts its buffered
    rows into the db using the given statement, then commits the transaction.
    """

    def __init__(
        self,
        item_mapper: ItemToDbRowMapper[T],
        max_buffer_len: int,
        connection_lender: ConnectionLender,
        insertion_statement: str,
    ) -> None:
        super().__init__(item_mapper=item_mapper, max_buffer_len=max_buffer_len)
        self._connection_lender = connection_lender
        self._insertion_statement = insertion_statement

    def flush(self) -> None:
        try:
            connection = self._connection_lender()

            with closing(connection.cursor()) as cursor:
                cursor.executemany(self._insertion_statement, self._buffer)

            connection.commit()
        finally:
            super().flush()


class BufferedDbSerializer(DelayedSerializer[Any]):
    """
    Buffered serializer for storing multiple kinds of objects into a db.

    In particular, you'll probably want to use it as follows:

    1. instantiate it anda save it to a variable - for example, "my_serializer"

    2. register serializers via its @my_serializer.register() decorator

    3. call its request_serialize() method, just like any other delayed serializer

    When flush() is called - directly or at the end of a "with" block, all the internal
    serializers are flushed and their buffers written to DB; exceptions are ignored, but logged
    if in __debug__.

    It is recommended to always use "INSERT OR IGNORE" statements.
    """

    def __init__(self, connection_lender: ConnectionLender) -> None:
        self._connection_lender = connection_lender
        self._composite_serializer = CompositeDelayedSerializer[Any]()

    def request_serialize(self, item: Any) -> None:
        self._composite_serializer.request_serialize(item)

    def flush(self) -> None:
        self._composite_serializer.flush()

    def register[T](
        self, insertion_statement: str, max_buffer_len: int = 3000
    ) -> Callable[[ItemToDbRowMapper[T]], ItemToDbRowMapper[T]]:
        """
        Tells the serializer how to serialize a given object type into db.

        register() must be used as a decorator on any function capable of mapping an object
        to a tuple used as a database row; the only mandatory argument to the decorator is
        the related SQL insertion statement: it is worth noting that such statement should be
        not just INSERT, but INSERT OR IGNORE, to ensure that as many rows as possible are
        inserted into the db by the bulk operation performed by the internal serializer.

        The max_buffer_len argument states how many rows should be buffered before automatic
        flushing.

        Please, refer to the tests for detailed examples.
        """

        def decorator(
            item_mapper: ItemToDbRowMapper[T],
        ) -> ItemToDbRowMapper[T]:
            serializer = ItemToRowSerializer(
                item_mapper=item_mapper,
                max_buffer_len=max_buffer_len,
                connection_lender=self._connection_lender,
                insertion_statement=insertion_statement,
            )

            mapper_parameter = get_single_parameter(item_mapper)
            item_type = mapper_parameter.annotation
            if not item_type:
                raise ValueError(
                    "The mapper does not explicitly declare a type annotation for its parameter"
                )

            self._composite_serializer.add_serializer(
                item_type=item_type, serializer=serializer
            )

            return item_mapper

        return decorator
