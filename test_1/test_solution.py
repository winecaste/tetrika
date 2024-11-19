import pytest
from solution import strict

def test_correct_types():
    @strict
    def test_func(a: int, b: str) -> bool:
        return len(b) > a

    assert test_func(2, "hello")

def test_incorrect_int_type():
    @strict
    def test_func(a: int, b: str) -> bool:
        return len(b) > a

    with pytest.raises(TypeError):
        test_func("2", "hello")

def test_incorrect_str_type():
    @strict
    def test_func(a: int, b: str) -> bool:
        return len(b) > a

    with pytest.raises(TypeError):
        test_func(2, 5)

def test_float_and_bool():
    @strict
    def test_func(a: float, b: bool) -> float:
        return a * (1 if b else -1)

    assert test_func(3.14, True) == 3.14
    assert test_func(3.14, False) == -3.14

    with pytest.raises(TypeError):
        test_func("3.14", True)

    with pytest.raises(TypeError):
        test_func(3.14, 1)
