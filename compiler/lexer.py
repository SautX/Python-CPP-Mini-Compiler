
# compiler/lexer.py

from dataclasses import dataclass


@dataclass
class Token:
    type: str
    value: object
    line: int
    column: int

    def __repr__(self):
        return (
            f"Token({self.type}, {self.value!r}, "
            f"line={self.line}, column={self.column})"
        )


class LexerError(Exception):
    pass


class Lexer:

    KEYWORDS = {
        "and": "AND",
        "or": "OR",
        "not": "NOT",
        "True": "BOOL",
        "False": "BOOL",
        "print": "PRINT",
    }

    TWO_CHAR_OPERATORS = {
        "==": "EQ",
        "!=": "NE",
        "<=": "LE",
        ">=": "GE",
        "//": "FLOOR_DIV",
        "**": "POWER",
        "<<": "LSHIFT",
        ">>": "RSHIFT",
    }

    ONE_CHAR_OPERATORS = {
        "+": "PLUS",
        "-": "MINUS",
        "*": "MULTIPLY",
        "/": "DIVIDE",
        "%": "MODULO",
        "<": "LT",
        ">": "GT",
        "&": "BIT_AND",
        "|": "BIT_OR",
        "^": "BIT_XOR",
        "~": "BIT_NOT",
        "=": "ASSIGN",
    }

    PUNCTUATION = {
        "(": "LPAREN",
        ")": "RPAREN",
        ",": "COMMA",
    }

    def __init__(self, source):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1

    def current(self):
        if self.position >= len(self.source):
            return None
        return self.source[self.position]

    def peek(self, offset=1):
        pos = self.position + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]

    def advance(self):
        char = self.current()

        if char is None:
            return None

        self.position += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def skip_whitespace(self):
        while self.current() is not None:
            if self.current() in " \t\r":
                self.advance()
            else:
                break

    def skip_comment(self):
        while self.current() is not None:
            if self.current() == "\n":
                break
            self.advance()

    def read_number(self):
        start_line = self.line
        start_column = self.column

        number = ""
        has_dot = False
        has_exponent = False

        # Integer and decimal part
        while self.current() is not None:
            char = self.current()

            if char.isdigit():
                number += self.advance()

            elif char == "." and not has_dot and not has_exponent:
                # Do not consume the first dot of a range-like expression.
                if self.peek() == ".":
                    break

                has_dot = True
                number += self.advance()

            else:
                break

        # Scientific notation: 1.5e3, 2E-4
        if self.current() in ("e", "E"):
            has_exponent = True
            number += self.advance()

            if self.current() in ("+", "-"):
                number += self.advance()

            if self.current() is None or not self.current().isdigit():
                raise LexerError(
                    f"Invalid exponent at line {self.line}, "
                    f"column {self.column}"
                )

            while self.current() is not None and self.current().isdigit():
                number += self.advance()

        if has_dot or has_exponent:
            value = float(number)
            token_type = "FLOAT"
        else:
            value = int(number)
            token_type = "INTEGER"

        return Token(token_type, value, start_line, start_column)

    def read_identifier(self):
        start_line = self.line
        start_column = self.column

        identifier = ""

        while self.current() is not None:
            char = self.current()

            if char.isalnum() or char == "_":
                identifier += self.advance()
            else:
                break

        token_type = self.KEYWORDS.get(identifier, "IDENTIFIER")

        if token_type == "BOOL":
            value = identifier == "True"
        else:
            value = identifier

        return Token(token_type, value, start_line, start_column)

    def tokenize(self):
        tokens = []

        while self.current() is not None:

            self.skip_whitespace()

            char = self.current()

            if char is None:
                break

            if char == "#":
                self.skip_comment()
                continue

            if char == "\n":
                tokens.append(
                    Token("NEWLINE", "\n", self.line, self.column)
                )
                self.advance()
                continue

            if char.isdigit():
                tokens.append(self.read_number())
                continue

            if char.isalpha() or char == "_":
                tokens.append(self.read_identifier())
                continue

            start_line = self.line
            start_column = self.column

            pair = char + (self.peek() or "")

            if pair in self.TWO_CHAR_OPERATORS:
                token_type = self.TWO_CHAR_OPERATORS[pair]
                self.advance()
                self.advance()

                tokens.append(
                    Token(token_type, pair, start_line, start_column)
                )
                continue

            if char in self.ONE_CHAR_OPERATORS:
                token_type = self.ONE_CHAR_OPERATORS[char]
                self.advance()

                tokens.append(
                    Token(token_type, char, start_line, start_column)
                )
                continue

            if char in self.PUNCTUATION:
                token_type = self.PUNCTUATION[char]
                self.advance()

                tokens.append(
                    Token(token_type, char, start_line, start_column)
                )
                continue

            raise LexerError(
                f"Unexpected character {char!r} "
                f"at line {self.line}, column {self.column}"
            )

        tokens.append(
            Token("EOF", None, self.line, self.column)
        )

        return tokens


def tokenize(source):
    return Lexer(source).tokenize()
