
import unittest

from compiler.frontend import Frontend


class TestParserAndFrontend(unittest.TestCase):

    def setUp(self):
        self.frontend = Frontend()

    def compile_source(self, source):
        return self.frontend.compile(source)

    def test_integer_assignment(self):
        result = self.compile_source("x = 10")
        self.assertTrue(result["success"])

    def test_float_assignment(self):
        result = self.compile_source("x = 10.5")
        self.assertTrue(result["success"])

    def test_arithmetic_expression(self):
        result = self.compile_source("x = (10 + 5) * 2")
        self.assertTrue(result["success"])

    def test_comparison_expression(self):
        result = self.compile_source("x = 10 > 5")
        self.assertTrue(result["success"])

    def test_logical_expression(self):
        result = self.compile_source("x = True and False")
        self.assertTrue(result["success"])

    def test_bitwise_expression(self):
        result = self.compile_source("x = 10 & 5")
        self.assertTrue(result["success"])

    def test_shift_expression(self):
        result = self.compile_source("x = 2 << 3")
        self.assertTrue(result["success"])

    def test_unary_expression(self):
        result = self.compile_source("x = -10")
        self.assertTrue(result["success"])

    def test_boolean_literals(self):
        result = self.compile_source("x = True")
        self.assertTrue(result["success"])

    def test_print_statement(self):
        result = self.compile_source("print(10 + 20)")
        self.assertTrue(result["success"])

    def test_invalid_syntax(self):
        result = self.compile_source("x = ")
        self.assertFalse(result["success"])

    def test_multiple_statements(self):
        source = """
a = 10
b = 20
c = a + b
print(c)
"""
        result = self.compile_source(source)
        self.assertTrue(result["success"])


if __name__ == "__main__":
    unittest.main()
