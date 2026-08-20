from logging import getLogger
from os import unlink
from os.path import join
from shutil import rmtree
from tempfile import gettempdir
from typing import Self
from uuid import uuid4

from ...functional import Producer


class TemporaryPath(str):
    """
    String containing the path to a temporary file or directory.

    When instantiated, it refers to a unique, non-existing path within the system's temporary
    directory.

    You can use it to create a file or a directory; furthermore, you can - and most often should -
    instantiate it in the header of a "with" block, with the guarantee that the related
    file/directory will be deleted in the end; alternatively, you can call its try_to_remove()
    method when in need, or just do nothing about it - for example, if you want to move the file
    at the end of some processing.

    Cleanup exceptions are ignored; they are logged, but only when in __debug__.

    To use the class, you need to pass it a generator for its basename; in particular, for
    simplicity, you might want to use its Uuid4TemporaryPath subclass instead.

    If you don't ask for deletion explicitly - either via a "with" block or by calling
    try_to_remove() in a finally block - there will be no automatic deletion.
    """

    _logger = getLogger("TemporaryPath")

    def __new__(cls, basename_producer: Producer[str]) -> Self:
        """
        Creates the temporary path.

        The basename producer must be capable of creating a reasonably unique name that would
        reside within the temporary directory returned by gettempdir().
        """
        return str.__new__(cls, join(gettempdir(), basename_producer()))

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.try_to_remove()

    def try_to_remove(self) -> None:
        """
        Tries to remove the file/directory related to the temporary path.

        You usually won't need to call this method - prefer a "with" block instead.
        """
        try:
            if __debug__:
                self._logger.info("Trying to delete file named: %s", self)

            unlink(self)

            if __debug__:
                self._logger.info("Temporary file deleted!")

            return
        except OSError:
            if __debug__:
                self._logger.info("Could not delete the temporary name as a file")

        try:
            if __debug__:
                self._logger.info("Trying to delete directory tree: %s", self)

            rmtree(self)

            if __debug__:
                self._logger.info("Temporary directory tree deleted!")

            return
        except OSError:
            if __debug__:
                self._logger.info(
                    "Could not delete the temporary name as a directory tree"
                )


class Uuid4TemporaryPath(TemporaryPath):
    """
    Temporary path whose basename is a UUID.
    """

    def __new__(cls, extension_including_dot: str = "") -> Self:
        return TemporaryPath.__new__(cls, lambda: f"{uuid4()}{extension_including_dot}")
