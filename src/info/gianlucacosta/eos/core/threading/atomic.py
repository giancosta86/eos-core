from threading import Lock

from ..functional import Mapper


class Atomic[T]:
    """
    Value that can only be accessed and changed atomically.

    Simultaneous access to the internal value is delayed by a Lock.
    """

    def __init__(self, initial_value: T):
        self._value = initial_value
        self._lock = Lock()

    def get(self) -> T:
        """
        Returns the value.
        """
        with self._lock:
            return self._value

    def set(self, new_value: T) -> None:
        """
        Sets the value.
        """
        with self._lock:
            self._value = new_value

    def get_then_set(self, new_value: T) -> T:
        """
        Atomically, sets the value but returns the old one.
        """
        with self._lock:
            old_value = self._value
            self._value = new_value
            return old_value

    def get_then_map(self, mapper: Mapper[T, T]) -> T:
        """
        Atomically, sets the new value via a mapper, but returns the old value.
        """
        with self._lock:
            old_value = self._value
            self._value = mapper(old_value)
            return old_value

    def map_then_get(self, mapper: Mapper[T, T]) -> T:
        """
        Atomically, sets the new value via a mapper, returning such new value.
        """
        with self._lock:
            self._value = mapper(self._value)
            return self._value

    def map(self, mapper: Mapper[T, T]) -> None:
        """
        Atomically, applies the mapper to the current value, setting the result as the new value.
        """
        with self._lock:
            self._value = mapper(self._value)
