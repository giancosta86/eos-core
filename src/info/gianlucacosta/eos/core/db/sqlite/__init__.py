from contextlib import closing
from sqlite3 import Connection, connect

from ...functional import Lender, Producer

type ConnectionFactory = Producer[Connection]
"""
Function returning a SQLite connection that must be closed by the caller
"""


type ConnectionLender = Lender[Connection]
"""
Function returning a connection that should NOT be closed by the caller
"""


def create_memory_db() -> closing[Connection]:
    """
    Returns a connection to an in-memory SQLite db.
    """
    return closing(connect(":memory:"))
