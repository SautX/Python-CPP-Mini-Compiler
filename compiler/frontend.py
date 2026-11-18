from types import SimpleNamespace

from .lexer import tokenize
from .parser import (
    parse_tokens,
    Number,
    Variable,
    BinaryOperation,
    UnaryOperation,
    Assignment,
    PrintStatement
)

from .ast_generator import generate_ast
from .intermediate_code import IRGenerator
from .bytecode import Instruction, Program
from .optimizer import optimize_program


OPERATOR_MAP = {
    "+": "ADD",
    "-": "SUB",
    "*": "MUL",
    "/": "DIV",
    "%": "MOD"
}


def convert_expression(node):

    if isinstance(node, Number):

        return SimpleNamespace(
            operation="CONST",
            value=node.value
        )

    if isinstance(node, Variable):

        return SimpleNamespace(
            operation="VAR",
            value=node.name
        )

    if isinstance(node, UnaryOperation):

        return SimpleNamespace(
            operation="NEG",
            operand=convert_expression(node.operand)
        )

    if isinstance(node, BinaryOperation):

        return SimpleNamespace(
            operation=OPERATOR_MAP[node.operator],
            left=convert_expression(node.left),
            right=convert_expression(node.right)
        )

    raise TypeError("Unsupported expression")


def compile_source_to_bytecode(source):

    # 1. Lexical analysis
    tokens = tokenize(source)

    # 2. Syntax analysis
    statements = parse_tokens(tokens)

    # 3. AST generation
    python_ast = generate_ast(statements)

    # 4. Convert parsed statements into IR input
    ir_statements = []

    for statement in statements:

        if isinstance(statement, Assignment):

            ir_statements.append((
                "ASSIGN",
                statement.name,
                convert_expression(statement.value)
            ))

        elif isinstance(statement, PrintStatement):

            ir_statements.append((
                "PRINT",
                convert_expression(statement.value)
            ))

    # 5. Intermediate code generation
    generator = IRGenerator()

    ir_program = generator.generate(ir_statements)

    # 6. Convert IR into custom bytecode
    program = Program(
        constants=ir_program.constants,
        variables=ir_program.variables
    )

    for instruction in ir_program.instructions:

        program.instructions.append(
            Instruction(
                instruction.operation,
                instruction.operand
            )
        )

    # 7. Optimization
    program = optimize_program(program)

    return program


def generate_python_ast(source):

    tokens = tokenize(source)

    statements = parse_tokens(tokens)

    return generate_ast(statements)