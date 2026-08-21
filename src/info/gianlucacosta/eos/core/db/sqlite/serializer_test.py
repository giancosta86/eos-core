from contextlib import closing
from dataclasses import dataclass
from sqlite3 import Connection

from pytest import raises

from . import create_memory_db
from .serializer import BufferedDbSerializer


@dataclass
class Bear:
    name: str
    age: int


def create_schema(connection: Connection) -> None:
    with closing(connection.cursor()) as cursor:
        cursor.executescript("""
        CREATE TABLE bears (
            name TEXT NOT NULL PRIMARY KEY,
            age INT NOT NULL
        )
        """)


def create_serializer(
    connection: Connection, max_buffer_len: int
) -> BufferedDbSerializer:
    serializer = BufferedDbSerializer(lambda: connection)

    @serializer.register(
        """
        INSERT INTO bears
        (name, age)
        VALUES
        (?, ?)
        """,
        max_buffer_len=max_buffer_len,
    )
    def serialize_bear(bear: Bear):
        return (bear.name, bear.age)

    return serializer


def basic_flow(flush: bool, expected_query_result: list[tuple[str, int]]):
    with create_memory_db() as connection:
        create_schema(connection)

        serializer = create_serializer(connection, max_buffer_len=90)

        yogi = Bear("Yogi", 35)
        bubu = Bear("Bubu", 32)

        serializer.request_serialize(yogi)
        serializer.request_serialize(bubu)

        if flush:
            serializer.flush()

        with closing(connection.cursor()) as cursor:
            cursor.execute("SELECT name, age FROM bears ORDER BY name")

            assert cursor.fetchall() == expected_query_result


def test_serializer_with_registered_class_without_flushing():
    basic_flow(flush=False, expected_query_result=[])


def test_serializer_with_registered_class_with_flushing():
    basic_flow(flush=True, expected_query_result=[("Bubu", 32), ("Yogi", 35)])


def test_serializer_with_the_with_block():
    with create_memory_db() as connection:
        create_schema(connection)

        with create_serializer(connection, max_buffer_len=90) as serializer:

            yogi = Bear("Yogi", 35)
            bubu = Bear("Bubu", 32)

            serializer.request_serialize(yogi)
            serializer.request_serialize(bubu)

        with closing(connection.cursor()) as cursor:
            cursor.execute("SELECT name, age FROM bears ORDER BY name")

            assert cursor.fetchall() == [("Bubu", 32), ("Yogi", 35)]


def test_serializer_with_unitary_buffer_size():
    with create_memory_db() as connection:
        create_schema(connection)

        serializer = create_serializer(connection, max_buffer_len=1)

        yogi = Bear("Yogi", 35)
        bubu = Bear("Bubu", 32)

        serializer.request_serialize(yogi)
        serializer.request_serialize(bubu)

        with closing(connection.cursor()) as cursor:
            cursor.execute("SELECT name, age FROM bears ORDER BY name")

            assert cursor.fetchall() == [("Bubu", 32), ("Yogi", 35)]


def test_registering_type_twice():
    with create_memory_db() as connection:
        create_schema(connection)

        serializer = BufferedDbSerializer(lambda: connection)

        @serializer.register("""
            INSERT INTO bears
            (name, age)
            VALUES
            (?, ?)
            """)
        def serialize_bear_once(bear: Bear):
            return (bear.name, bear.age)

        with raises(KeyError):

            @serializer.register("""
                INSERT INTO bears
                (name, age)
                VALUES
                (?, ?)
                """)
            def serialize_bear_twice(bear: Bear):
                return (bear.name, bear.age)


def test_serializing_unregistered_type():
    with create_memory_db() as connection:
        create_schema(connection)

        serializer = BufferedDbSerializer(lambda: connection)

        with raises(KeyError):
            serializer.request_serialize(Bear("Yogi", 35))
