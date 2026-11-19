
# compiler/ast_generator.py

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ASTNode:
    pass


@dataclass
class Program(ASTNode):
    body: list = field(default_factory=list)


@dataclass
class Assignment(ASTNode):
    name: str
    value: ASTNode


@dataclass
class Print(ASTNode):
    arguments: list


@dataclass
class ExpressionStatement(ASTNode):
    expression: ASTNode


@dataclass
class IntegerLiteral(ASTNode):
    value: int


@dataclass
class FloatLiteral(ASTNode):
    value: float


@dataclass
class BooleanLiteral(ASTNode):
    value: bool


@dataclass
class Identifier(ASTNode):
    name: str


@dataclass
class UnaryExpression(ASTNode):
    operator: str
    operand: ASTNode


@dataclass
class BinaryExpression(ASTNode):
    operator: str
    left: ASTNode
    right: ASTNode


class ASTGenerator:

    def generate(self, parsed_data):
        if not isinstance(parsed_data, dict):
            raise TypeError("Expected parser dictionary")

        node_type = parsed_data.get("type")

        if node_type == "Program":
            return Program(
                body=[
                    self.generate(statement)
                    for statement in parsed_data["body"]
                ]
            )

        if node_type == "Assignment":
            return Assignment(
                name=parsed_data["name"],
                value=self.generate(parsed_data["value"])
            )

        if node_type == "Print":
            return Print(
                arguments=[
                    self.generate(argument)
                    for argument in parsed_data["arguments"]
                ]
            )

        if node_type == "ExpressionStatement":
            return ExpressionStatement(
                expression=self.generate(
                    parsed_data["expression"]
                )
            )

        if node_type == "IntegerLiteral":
            return IntegerLiteral(
                value=int(parsed_data["value"])
            )

        if node_type == "FloatLiteral":
            return FloatLiteral(
                value=float(parsed_data["value"])
            )

        if node_type == "BooleanLiteral":
            return BooleanLiteral(
                value=bool(parsed_data["value"])
            )

        if node_type == "Identifier":
            return Identifier(
                name=parsed_data["name"]
            )

        if node_type == "UnaryExpression":
            return UnaryExpression(
                operator=parsed_data["operator"],
                operand=self.generate(parsed_data["operand"])
            )

        if node_type == "BinaryExpression":
            return BinaryExpression(
                operator=parsed_data["operator"],
                left=self.generate(parsed_data["left"]),
                right=self.generate(parsed_data["right"])
            )

        raise ValueError(
            f"Unknown AST node type: {node_type}"
        )


def generate_ast(parsed_data):
    return ASTGenerator().generate(parsed_data)
