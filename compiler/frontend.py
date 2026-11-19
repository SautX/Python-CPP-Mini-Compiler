
# compiler/frontend.py

from .lexer import Lexer, LexerError
from .parser import Parser, ParserError
from .ast_generator import (
    ASTGenerator,
    Program,
    Assignment,
    Print,
    ExpressionStatement,
    IntegerLiteral,
    FloatLiteral,
    BooleanLiteral,
    Identifier,
    UnaryExpression,
    BinaryExpression
)


class FrontendError(Exception):
    pass


class TypeChecker:

    def __init__(self):
        self.symbol_table = {}

    INTEGER_ONLY_OPERATORS = {
        "&", "|", "^", "~", "<<", ">>"
    }

    COMPARISON_OPERATORS = {
        "==", "!=", "<", ">", "<=", ">="
    }

    LOGICAL_OPERATORS = {
        "and", "or"
    }

    ARITHMETIC_OPERATORS = {
        "+", "-", "*", "/", "//", "%", "**"
    }

    def infer_type(self, node):

        if isinstance(node, IntegerLiteral):
            return "int"

        if isinstance(node, FloatLiteral):
            return "float"

        if isinstance(node, BooleanLiteral):
            return "bool"

        if isinstance(node, Identifier):
            if node.name not in self.symbol_table:
                raise FrontendError(
                    f"Undefined variable: {node.name}"
                )

            return self.symbol_table[node.name]

        if isinstance(node, UnaryExpression):
            operand_type = self.infer_type(node.operand)

            if node.operator == "not":
                return "bool"

            if node.operator == "~":
                if operand_type != "int":
                    raise FrontendError(
                        "Bitwise NOT requires an integer"
                    )

                return "int"

            if node.operator in ("+", "-"):
                if operand_type not in ("int", "float"):
                    raise FrontendError(
                        f"Unary {node.operator} requires "
                        "an integer or float"
                    )

                return operand_type

        if isinstance(node, BinaryExpression):
            left_type = self.infer_type(node.left)
            right_type = self.infer_type(node.right)
            operator = node.operator

            if operator in self.COMPARISON_OPERATORS:
                if left_type not in ("int", "float", "bool"):
                    raise FrontendError(
                        "Unsupported comparison operand"
                    )

                if right_type not in ("int", "float", "bool"):
                    raise FrontendError(
                        "Unsupported comparison operand"
                    )

                if operator in ("<", ">", "<=", ">="):
                    if "bool" in (left_type, right_type):
                        raise FrontendError(
                            "Boolean ordering comparisons "
                            "are not supported"
                        )

                return "bool"

            if operator in self.LOGICAL_OPERATORS:
                return "bool"

            if operator in self.INTEGER_ONLY_OPERATORS:
                if left_type != "int" or right_type != "int":
                    raise FrontendError(
                        f"Operator {operator} requires "
                        "integer operands"
                    )

                return "int"

            if operator in self.ARITHMETIC_OPERATORS:
                if left_type not in ("int", "float"):
                    raise FrontendError(
                        f"Invalid left operand for {operator}"
                    )

                if right_type not in ("int", "float"):
                    raise FrontendError(
                        f"Invalid right operand for {operator}"
                    )

                if operator == "/":
                    return "float"

                if operator == "//":
                    if left_type == "float" or right_type == "float":
                        return "float"
                    return "int"

                if operator == "%":
                    if left_type == "float" or right_type == "float":
                        return "float"
                    return "int"

                if operator == "**":
                    if left_type == "float" or right_type == "float":
                        return "float"
                    return "int"

                if left_type == "float" or right_type == "float":
                    return "float"

                return "int"

            raise FrontendError(
                f"Unsupported binary operator: {operator}"
            )

        raise FrontendError(
            f"Cannot infer type for {type(node).__name__}"
        )

    def check_statement(self, statement):

        if isinstance(statement, Assignment):
            value_type = self.infer_type(statement.value)

            self.symbol_table[statement.name] = value_type

            return value_type

        if isinstance(statement, Print):
            for argument in statement.arguments:
                self.infer_type(argument)

            return "void"

        if isinstance(statement, ExpressionStatement):
            return self.infer_type(statement.expression)

        raise FrontendError(
            f"Unsupported statement: {type(statement).__name__}"
        )

    def check(self, program):

        if not isinstance(program, Program):
            raise FrontendError("Expected a Program AST")

        for statement in program.body:
            self.check_statement(statement)

        return self.symbol_table.copy()


class Frontend:

    def __init__(self):
        self.tokens = []
        self.parsed_data = None
        self.ast = None
        self.type_checker = TypeChecker()

    def tokenize(self, source):
        lexer = Lexer(source)
        self.tokens = lexer.tokenize()
        return self.tokens

    def parse(self, source):
        parser = Parser(source)
        self.parsed_data = parser.parse()
        return self.parsed_data

    def generate_ast(self, parsed_data):
        generator = ASTGenerator()
        self.ast = generator.generate(parsed_data)
        return self.ast

    def type_check(self, ast):
        self.type_checker = TypeChecker()
        return self.type_checker.check(ast)

    def compile(self, source):

        try:
            # Stage 1: Lexical analysis
            tokens = self.tokenize(source)

            # Stage 2: Syntax analysis
            parsed_data = self.parse(source)

            # Stage 3: AST generation
            ast = self.generate_ast(parsed_data)

            # Stage 4: Static type checking
            symbol_table = self.type_check(ast)

            return {
                "success": True,
                "tokens": tokens,
                "parsed_data": parsed_data,
                "ast": ast,
                "symbol_table": symbol_table
            }

        except (LexerError, ParserError, FrontendError) as error:
            return {
                "success": False,
                "error": str(error),
                "tokens": self.tokens,
                "parsed_data": self.parsed_data,
                "ast": self.ast,
                "symbol_table": {}
            }


def compile_source(source):
    return Frontend().compile(source)
