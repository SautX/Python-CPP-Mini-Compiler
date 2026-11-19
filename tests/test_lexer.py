
import unittest

from compiler.lexer import tokenize


class TestLexer(unittest.TestCase):

    def get_values(self, source):
        tokens = tokenize(source)
        return [token.value for token in tokens]

    def test_integer(self):
        self.assertIn(100, self.get_values("x = 100"))

    def test_float(self):
        self.assertIn(10.5, self.get_values("x = 10.5"))

    def test_identifier(self):
        self.assertIn("total", self.get_values("total = 50"))

    def test_arithmetic_operators(self):
        values = self.get_values("x = a + b - c * d / e")
        for operator in ["+", "-", "*", "/"]:
            self.assertIn(operator, values)

    def test_comparison_operators(self):
        values = self.get_values("x = a >= b")
        self.assertIn(">=", values)

    def test_logical_operators(self):
        values = self.get_values("x = a and b or not c")
        for operator in ["and", "or", "not"]:
            self.assertIn(operator, values)

    def test_bitwise_operators(self):
        values = self.get_values("x = a & b | c ^ d")
        for operator in ["&", "|", "^"]:
            self.assertIn(operator, values)

    def test_shift_operators(self):
        values = self.get_values("x = a << 2")
        self.assertIn("<<", values)

    def test_boolean_literals(self):
        values = self.get_values("x = True")
        self.assertIn("True", values)

    def test_print_keyword(self):
        values = self.get_values("print(100)")
        self.assertIn("print", values)


if __name__ == "__main__":
    unittest.main()
