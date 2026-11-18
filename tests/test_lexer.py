
import unittest

from compiler.lexer import Lexer


class TestLexer(unittest.TestCase):

    def get_tokens(self, source):
        lexer = Lexer(source)
        return lexer.tokenize()

    def test_number(self):
        tokens = self.get_tokens("123")
        self.assertTrue(any(token.value == "123" for token in tokens))

    def test_identifier(self):
        tokens = self.get_tokens("variable")
        self.assertTrue(
            any(token.value == "variable" for token in tokens)
        )

    def test_addition(self):
        tokens = self.get_tokens("a + b")
        values = [token.value for token in tokens]
        self.assertIn("+", values)

    def test_assignment(self):
        tokens = self.get_tokens("a = 10")
        values = [token.value for token in tokens]
        self.assertIn("=", values)

    def test_parentheses(self):
        tokens = self.get_tokens("(10 + 20)")
        values = [token.value for token in tokens]
        self.assertIn("(", values)
        self.assertIn(")", values)


if __name__ == "__main__":
    unittest.main()
