
# compiler/parser.py

from .lexer import Lexer


class ParserError(Exception):
    pass


class Parser:

    # Higher number means higher precedence.
    PRECEDENCE = {
        "OR": 1,
        "AND": 2,

        "EQ": 3,
        "NE": 3,
        "LT": 3,
        "GT": 3,
        "LE": 3,
        "GE": 3,

        "BIT_OR": 4,
        "BIT_XOR": 5,
        "BIT_AND": 6,

        "LSHIFT": 7,
        "RSHIFT": 7,

        "PLUS": 8,
        "MINUS": 8,

        "MULTIPLY": 9,
        "DIVIDE": 9,
        "FLOOR_DIV": 9,
        "MODULO": 9,

        "POWER": 11,
    }

    BINARY_OPERATORS = {
        "OR": "or",
        "AND": "and",

        "EQ": "==",
        "NE": "!=",
        "LT": "<",
        "GT": ">",
        "LE": "<=",
        "GE": ">=",

        "BIT_OR": "|",
        "BIT_XOR": "^",
        "BIT_AND": "&",

        "LSHIFT": "<<",
        "RSHIFT": ">>",

        "PLUS": "+",
        "MINUS": "-",

        "MULTIPLY": "*",
        "DIVIDE": "/",
        "FLOOR_DIV": "//",
        "MODULO": "%",

        "POWER": "**",
    }

    def __init__(self, source):
        self.tokens = Lexer(source).tokenize()
        self.position = 0

    def current(self):
        if self.position >= len(self.tokens):
            return self.tokens[-1]

        return self.tokens[self.position]

    def peek(self, offset=1):
        position = self.position + offset

        if position >= len(self.tokens):
            return self.tokens[-1]

        return self.tokens[position]

    def advance(self):
        token = self.current()

        if token.type != "EOF":
            self.position += 1

        return token

    def match(self, *types):
        if self.current().type in types:
            return self.advance()

        return None

    def expect(self, token_type):
        token = self.current()

        if token.type != token_type:
            raise ParserError(
                f"Expected {token_type}, got {token.type} "
                f"at line {token.line}, column {token.column}"
            )

        return self.advance()

    def skip_newlines(self):
        while self.current().type == "NEWLINE":
            self.advance()

    def parse(self):
        statements = []

        self.skip_newlines()

        while self.current().type != "EOF":
            statements.append(self.parse_statement())

            if self.current().type not in ("NEWLINE", "EOF"):
                token = self.current()
                raise ParserError(
                    f"Unexpected token {token.value!r} "
                    f"at line {token.line}"
                )

            self.skip_newlines()

        return {
            "type": "Program",
            "body": statements
        }

    def parse_statement(self):

        # print(expression)
        if self.current().type == "PRINT":
            return self.parse_print()

        # variable = expression
        if (
            self.current().type == "IDENTIFIER"
            and self.peek().type == "ASSIGN"
        ):
            return self.parse_assignment()

        # Standalone expression
        expression = self.parse_expression()

        return {
            "type": "ExpressionStatement",
            "expression": expression
        }

    def parse_print(self):
        self.expect("PRINT")
        self.expect("LPAREN")

        arguments = []

        if self.current().type != "RPAREN":
            arguments.append(self.parse_expression())

            while self.match("COMMA"):
                arguments.append(self.parse_expression())

        self.expect("RPAREN")

        return {
            "type": "Print",
            "arguments": arguments
        }

    def parse_assignment(self):
        name = self.expect("IDENTIFIER").value

        self.expect("ASSIGN")

        value = self.parse_expression()

        return {
            "type": "Assignment",
            "name": name,
            "value": value
        }

    def parse_expression(self, min_precedence=1):
        left = self.parse_unary()

        while True:
            token = self.current()

            precedence = self.PRECEDENCE.get(token.type, -1)

            if precedence < min_precedence:
                break

            operator = self.advance()
            operator_value = self.BINARY_OPERATORS[operator.type]

            # Exponentiation is right-associative.
            if operator.type == "POWER":
                next_precedence = precedence
            else:
                next_precedence = precedence + 1

            right = self.parse_expression(next_precedence)

            left = {
                "type": "BinaryExpression",
                "operator": operator_value,
                "left": left,
                "right": right
            }

        return left

    def parse_unary(self):
        token = self.current()

        unary_operators = {
            "PLUS": "+",
            "MINUS": "-",
            "NOT": "not",
            "BIT_NOT": "~"
        }

        if token.type in unary_operators:
            operator = self.advance()

            # Python's exponentiation binds more tightly than
            # unary minus: -2**2 means -(2**2).
            if operator.type in ("PLUS", "MINUS"):
                operand = self.parse_expression(10)
            else:
                operand = self.parse_expression(10)

            return {
                "type": "UnaryExpression",
                "operator": unary_operators[operator.type],
                "operand": operand
            }

        return self.parse_primary()

    def parse_primary(self):
        token = self.current()

        if token.type == "INTEGER":
            self.advance()

            return {
                "type": "IntegerLiteral",
                "value": token.value
            }

        if token.type == "FLOAT":
            self.advance()

            return {
                "type": "FloatLiteral",
                "value": token.value
            }

        if token.type == "BOOL":
            self.advance()

            return {
                "type": "BooleanLiteral",
                "value": token.value
            }

        if token.type == "IDENTIFIER":
            self.advance()

            return {
                "type": "Identifier",
                "name": token.value
            }

        if self.match("LPAREN"):
            expression = self.parse_expression()
            self.expect("RPAREN")
            return expression

        raise ParserError(
            f"Unexpected token {token.type} "
            f"with value {token.value!r} "
            f"at line {token.line}, column {token.column}"
        )


def parse(source):
    return Parser(source).parse()
