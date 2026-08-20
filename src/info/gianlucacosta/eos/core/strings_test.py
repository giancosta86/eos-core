from .strings import strip_to_none


class TestStripToNone:
    def test_when_nonempty(self):
        assert strip_to_none("Dodo") == "Dodo"

    def test_when_nonempty_with_spaces(self):
        assert strip_to_none("    Dodo   ") == "Dodo"

    def test_when_empty(self):
        assert strip_to_none("") is None

    def test_when_spaces_only(self):
        assert strip_to_none("    ") is None

    def test_when_none(self):
        assert strip_to_none(None) is None
