from dataclasses import dataclass


@dataclass
class Number:
    value: int


@dataclass
class Variable:
    name: str


@dataclass
class BinaryOperation:
    left: object
    operator: str
    right: object


@dataclass
class UnaryOperation:
    operator: str
    operand: object


@dataclass
class Assignment:
    name: str
    value: object


@dataclass
class PrintStatement:
    value: object


class Parser:

    def __init__(self, tokens):

        self.tokens = tokens
        self.position = 0

    def current(self):

        return self.tokens[self.position]

    def advance(self):

        token = self.current()
        self.position += 1

        return token

    def expect(self, token_type):

        token = self.current()

        if token.type != token_type:

            raise SyntaxError(
                f"Expected {token_type}, "
                f"got {token.type} at line {token.line}"
            )

        return self.advance()

    def parse(self):

        statements = []

        while self.current().type != "EOF":

            if self.current().type == "NEWLINE":

                self.advance()
                continue

            statements.append(
                self.statement()
            )

            if self.current().type == "NEWLINE":
                self.advance()

            elif self.current().type != "EOF":
                raise SyntaxError(
                    "Expected newline between statements"
                )

        return statements

    def statement(self):

        if self.current().type == "IDENTIFIER":

            name = self.advance().value

            self.expect("ASSIGN")

            value = self.expression()

            return Assignment(name, value)

        elif self.current().type == "PRINT":

            self.advance()

            self.expect("LPAREN")

            value = self.expression()

            self.expect("RPAREN")

            return PrintStatement(value)

        raise SyntaxError(
            f"Invalid statement at line {self.current().line}"
        )

    def expression(self):

        node = self.term()

        while self.current().type in ("PLUS", "MINUS"):

            operator = self.advance().value

            right = self.term()

            node = BinaryOperation(
                node,
                operator,
                right
            )

        return node

    def term(self):

        node = self.factor()

        while self.current().type in (
            "MULTIPLY",
            "DIVIDE",
            "MODULO"
        ):

            operator = self.advance().value

            right = self.factor()

            node = BinaryOperation(
                node,
                operator,
                right
            )

        return node

    def factor(self):

        token = self.current()

        if token.type == "NUMBER":

            self.advance()

            return Number(int(token.value))

        if token.type == "IDENTIFIER":

            self.advance()

            return Variable(token.value)

        if token.type == "MINUS":

            self.advance()

            return UnaryOperation(
                "-",
                self.factor()
            )

        if token.type == "LPAREN":

            self.advance()

            node = self.expression()

            self.expect("RPAREN")

            return node

        raise SyntaxError(
            f"Unexpected token {token.type} at line {token.line}"
        )


def parse_tokens(tokens):

    return Parser(tokens).parse()