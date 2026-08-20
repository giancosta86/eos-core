from dataclasses import dataclass

from .reflection import get_single_parameter


@dataclass
class Bear:
    age: int


class TestGetSingleParameter:
    def test_with_single_arg_function_with_annotations(self):
        def my_function(yogi: Bear) -> int:
            return yogi.age

        parameter = get_single_parameter(my_function)
        assert parameter.name == "yogi"
        assert parameter.annotation == Bear
