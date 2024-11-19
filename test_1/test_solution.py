import unittest
from solution import strict

class TestStrictDecorator(unittest.TestCase):
    def test_correct_types(self):
        @strict
        def test_func(a: int, b: str) -> bool:
            return len(b) > a

        self.assertTrue(test_func(2, "hello"))

    def test_incorrect_int_type(self):
        @strict
        def test_func(a: int, b: str) -> bool:
            return len(b) > a

        with self.assertRaises(TypeError):
            test_func("2", "hello")

    def test_incorrect_str_type(self):
        @strict
        def test_func(a: int, b: str) -> bool:
            return len(b) > a

        with self.assertRaises(TypeError):
            test_func(2, 5)

    def test_float_and_bool(self):
        @strict
        def test_func(a: float, b: bool) -> float:
            return a * (1 if b else -1)

        self.assertEqual(test_func(3.14, True), 3.14)
        self.assertEqual(test_func(3.14, False), -3.14)

        with self.assertRaises(TypeError):
            test_func("3.14", True)

        with self.assertRaises(TypeError):
            test_func(3.14, 1)

if __name__ == '__main__':
    unittest.main()