import re
from os import makedirs
from os.path import basename, exists, isabs, join

from .temporary import Uuid4TemporaryPath


class TestUuid4TemporaryPath:
    def test_absolute(self):
        path = Uuid4TemporaryPath()
        assert isabs(path)

    def test_basename(self):
        path = Uuid4TemporaryPath()

        uuid_pattern = re.compile(
            r"[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"
        )

        assert uuid_pattern.match(basename(path))

    def test_with_extension(self):
        path = Uuid4TemporaryPath(extension_including_dot=".dodo")

        uuid_pattern_with_extension = re.compile(
            r"[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}\.dodo"
        )

        assert uuid_pattern_with_extension.match(basename(path))

    def test_when_context_unused(self):
        with Uuid4TemporaryPath() as path:
            assert not exists(path)

    def test_when_context_used_as_file(self):
        with Uuid4TemporaryPath() as file_path:
            with open(file_path, "w") as temp_file:
                temp_file.write("Hello, world! ^__^")

            assert exists(file_path)

        assert not exists(file_path)

    def test_when_context_used_as_dir(self):
        with Uuid4TemporaryPath() as dir_path:
            makedirs(dir_path)

            file_path = join(dir_path, "Test.txt")

            with open(file_path, "w") as temp_file:
                temp_file.write("Hello, world! ^__^")

            assert exists(file_path)

        assert not exists(file_path)
        assert not exists(dir_path)
