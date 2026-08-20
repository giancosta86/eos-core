from pytest import raises

from .ranges import InclusiveRange, RangedCounter


class TestRange:
    def test_creation_with_lower_less_than_upper(self):
        _ = InclusiveRange(lower=7, upper=90)

    def test_creation_with_lower_equal_to_upper(self):
        _ = InclusiveRange(lower=90, upper=90)

    def test_creation_with_lower_greater_than_upper(self):
        with raises(ValueError) as ex:
            _ = InclusiveRange(lower=1000, upper=90)

        assert ex.value.args == (1000, 90)


class TestRangedCounter:
    def test_creating_with_intermediate_value(self):
        counter = RangedCounter(InclusiveRange(7, 90), 18)
        assert counter.value == 18

    def test_creating_with_lower_value(self):
        counter = RangedCounter(InclusiveRange(7, 90), 7)
        assert counter.value == 7

    def test_creating_with_too_low_value(self):
        counter = RangedCounter(InclusiveRange(7, 90), -208)
        assert counter.value == 7

    def test_creating_with_upper_value(self):
        counter = RangedCounter(InclusiveRange(7, 90), 90)
        assert counter.value == 90

    def test_creating_with_too_high_value(self):
        counter = RangedCounter(InclusiveRange(7, 90), 1000)
        assert counter.value == 90

    def test_setting_to_intermediate_value(self):
        counter = RangedCounter(InclusiveRange(7, 90), 18)
        counter.value = 35
        assert counter.value == 35

    def test_setting_to_lower_value(self):
        counter = RangedCounter(InclusiveRange(7, 90), 18)
        counter.value = 7
        assert counter.value == 7

    def test_setting_to_too_low_value(self):
        counter = RangedCounter(InclusiveRange(7, 90), 18)
        counter.value = -50
        assert counter.value == 7

    def test_setting_to_upper_value(self):
        counter = RangedCounter(InclusiveRange(7, 90), 18)
        counter.value = 90
        assert counter.value == 90

    def test_setting_to_too_high_value(self):
        counter = RangedCounter(InclusiveRange(7, 90), 18)
        counter.value = 1000
        assert counter.value == 90
