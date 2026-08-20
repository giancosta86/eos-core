from collections.abc import Iterable
from multiprocessing.pool import Pool
from typing import Any, Self

from ...functional import AnyCallable, Consumer, Producer


class InThreadPool:
    """
    Class that mocks Python's Pool, by actually performing the operations within the very same
    thread.

    It is especially useful in contexts where sub-processes might be detrimental, especially in
    test cases in the Windows OS, or when debugging within an IDE.

    Therefore, a typical pattern consists in injecting a ProcessPoolFactory into classes and
    functions, actually letting the client decide what kind of pool they need.
    """

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        pass

    def apply(
        self,
        func: AnyCallable,
        args: Iterable[Any] | None = None,
        kwds: dict[Any, Any] | None = None,
    ) -> Any:
        return func(*(args if args is not None else []), **(kwds if kwds is not None else {}))

    def apply_async(
        self,
        func: AnyCallable,
        args: Iterable[Any] | None = None,
        kwds: dict[Any, Any] | None = None,
        callback: Consumer[Any] | None = None,
        error_callback: Consumer[Exception] | None = None,
    ) -> None:
        try:
            result = func(
                *(args if args is not None else []), **(kwds if kwds is not None else {})
            )

            if callback:
                callback(result)
        except Exception as ex:
            if error_callback:
                error_callback(ex)
            else:
                raise

    def close(self) -> None:
        pass

    def terminate(self) -> None:
        pass

    def join(self) -> None:
        pass


AnyProcessPool = Pool | InThreadPool
ProcessPoolFactory = Producer[AnyProcessPool]
