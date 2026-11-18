import ast

from .parser import (
    Number,
    Variable,
    BinaryOperation,
    UnaryOperation,
    Assignment,
    PrintStatement
)


BINARY_OPERATORS = {
    "+": ast.Add,
    "-": ast.Sub,
    "*": ast.Mult,
    "/": ast.Div,
    "%": ast.Mod
}


def generate_expression(node):

    if isinstance(node, Number):

        return ast.Constant(value=node.value)

    if isinstance(node, Variable):

        return ast.Name(
            id=node.name,
            ctx=ast.Load()
        )

    if isinstance(node, BinaryOperation):

        return ast.BinOp(
            left=generate_expression(node.left),
            op=BINARY_OPERATORS[node.operator](),
            right=generate_expression(node.right)
        )

    if isinstance(node, UnaryOperation):

        return ast.UnaryOp(
            op=ast.USub(),
            operand=generate_expression(node.operand)
        )

    raise TypeError("Unsupported expression node")


def generate_statement(node):

    if isinstance(node, Assignment):

        return ast.Assign(
            targets=[
                ast.Name(
                    id=node.name,
                    ctx=ast.Store()
                )
            ],
            value=generate_expression(node.value)
        )

    if isinstance(node, PrintStatement):

        return ast.Expr(
            value=ast.Call(
                func=ast.Name(
                    id="print",
                    ctx=ast.Load()
                ),
                args=[
                    generate_expression(node.value)
                ],
                keywords=[]
            )
        )

    raise TypeError("Unsupported statement")


def generate_ast(statements):

    module = ast.Module(
        body=[
            generate_statement(statement)
            for statement in statements
        ],
        type_ignores=[]
    )

    return ast.fix_missing_locations(module)