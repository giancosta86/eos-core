from collections.abc import Callable, Iterable
from queue import Queue

from ...functional import ContinuationProvider

type QueueWriter[T] = Callable[[Queue[T], ContinuationProvider, Iterable[T]], None]
type QueueReader[T] = Callable[[Queue[T], ContinuationProvider], None]
