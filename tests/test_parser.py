
import unittest

from compiler.lexer import Lexer
from compiler.parser import Parser


class TestParser(unittest.TestCase):

    def parse(self, source):
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()

    def test_assignment(self):
        result = self.parse("a = 10")
        self.assertEqual(len(result), 1)

    def test_print_statement(self):
        result = self.parse("print(10)")
        self.assertEqual(len(result), 1)

    def test_arithmetic_expression(self):
        result = self.parse("a = 10 + 20")
        self.assertEqual(len(result), 1)

    def test_multiple_statements(self):
        result = self.parse(
            "a = 10\n"
            "b = 20\n"
            "print(a + b)"
        )
        self.assertEqual(len(result), 3)

    def test_operator_precedence(self):
        result = self.parse("a = 10 + 20 * 2")
        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main()
