class CallbackExceptionCapturer:
    """
    Instances of this class can be passed to functions expecting (Exception|None) -> None
    callbacks.

    In particular, the optional exception is stored into a field - which can be inspected later
    via the "exception" property.

    It is especially handy in specific multi-threaded contexts such as testing.
    """

    def __init__(self) -> None:
        self._exception: Exception | None = None

    def __call__(self, exception: Exception | None) -> None:
        self._exception = exception

    @property
    def exception(self) -> Exception | None:
        return self._exception
