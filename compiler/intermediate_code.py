
# compiler/intermediate_code.py

from dataclasses import dataclass
from typing import Any

from .ast_generator import (
    Program,
    Assignment,
    Print,
    ExpressionStatement,
    IntegerLiteral,
    FloatLiteral,
    BooleanLiteral,
    Identifier,
    UnaryExpression,
    BinaryExpression,
)

from .bytecode import BytecodeProgram, Opcode


class IntermediateCodeError(Exception):
    pass


@dataclass
class IRInstruction:
    opcode: str
    operand: Any = None

    def __repr__(self):
        if self.operand is None:
            return self.opcode
        return f"{self.opcode} {self.operand}"


class IntermediateCodeGenerator:

    ARITHMETIC = {
        "+": ("ADD_INT", "ADD_FLOAT"),
        "-": ("SUB_INT", "SUB_FLOAT"),
        "*": ("MUL_INT", "MUL_FLOAT"),
        "/": ("DIV_FLOAT", "DIV_FLOAT"),
        "//": ("FLOOR_DIV_INT", "FLOOR_DIV_FLOAT"),
        "%": ("MOD_INT", "MOD_FLOAT"),
        "**": ("POWER_INT", "POWER_FLOAT"),
    }

    COMPARISON = {
        "==": "CMP_EQ",
        "!=": "CMP_NE",
        "<": "CMP_LT",
        ">": "CMP_GT",
        "<=": "CMP_LE",
        ">=": "CMP_GE",
    }

    BITWISE = {
        "&": "BIT_AND",
        "|": "BIT_OR",
        "^": "BIT_XOR",
        "<<": "LSHIFT",
        ">>": "RSHIFT",
    }

    def __init__(self):
        self.instructions = []
        self.symbol_table = {}
        self.label_counter = 0

    def emit(self, opcode, operand=None):
        self.instructions.append(IRInstruction(opcode, operand))

    def new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def mark_label(self, label):
        self.emit("LABEL", label)

    def compile(self, ast):
        if not isinstance(ast, Program):
            raise IntermediateCodeError("Expected Program AST")

        self.instructions = []
        self.symbol_table = {}
        self.label_counter = 0

        for statement in ast.body:
            self.compile_statement(statement)

        self.emit("HALT")

        return self.instructions

    def compile_statement(self, node):

        if isinstance(node, Assignment):
            value_type = self.compile_expression(node.value)

            name_index = node.name

            self.emit("STORE_VAR", name_index)
            self.symbol_table[node.name] = value_type
            return

        if isinstance(node, Print):
            for argument in node.arguments:
                value_type = self.compile_expression(argument)

                if value_type == "float":
                    self.emit("PRINT_FLOAT")
                elif value_type == "bool":
                    self.emit("PRINT_BOOL")
                else:
                    self.emit("PRINT_INT")
            return

        if isinstance(node, ExpressionStatement):
            self.compile_expression(node.expression)
            self.emit("POP")
            return

        raise IntermediateCodeError(
            f"Unsupported statement: {type(node).__name__}"
        )

    def compile_expression(self, node):

        if isinstance(node, IntegerLiteral):
            self.emit("LOAD_INT", node.value)
            return "int"

        if isinstance(node, FloatLiteral):
            self.emit("LOAD_FLOAT", node.value)
            return "float"

        if isinstance(node, BooleanLiteral):
            self.emit("LOAD_BOOL", node.value)
            return "bool"

        if isinstance(node, Identifier):
            if node.name not in self.symbol_table:
                raise IntermediateCodeError(
                    f"Undefined variable: {node.name}"
                )

            self.emit("LOAD_VAR", node.name)
            return self.symbol_table[node.name]

        if isinstance(node, UnaryExpression):
            operand_type = self.compile_expression(node.operand)
            operator = node.operator

            if operator == "not":
                self.emit("TO_BOOL")
                self.emit("LOGICAL_NOT")
                return "bool"

            if operator == "~":
                if operand_type != "int":
                    raise IntermediateCodeError(
                        "Bitwise NOT requires integer operand"
                    )
                self.emit("BIT_NOT")
                return "int"

            if operator == "-":
                self.emit("NEG")
                return operand_type

            if operator == "+":
                self.emit("POS")
                return operand_type

        if isinstance(node, BinaryExpression):
            operator = node.operator

            # Short-circuit logical operations.
            if operator in ("and", "or"):
                return self.compile_logical(node)

            left_type = self.compile_expression(node.left)
            right_type = self.compile_expression(node.right)

            if operator in self.COMPARISON:
                if "bool" in (left_type, right_type):
                    if operator not in ("==", "!="):
                        raise IntermediateCodeError(
                            "Boolean ordering comparison is unsupported"
                        )

                self.emit(self.COMPARISON[operator])
                return "bool"

            if operator in self.BITWISE:
                if left_type != "int" or right_type != "int":
                    raise IntermediateCodeError(
                        f"{operator} requires integer operands"
                    )
                self.emit(self.BITWISE[operator])
                return "int"

            if operator in self.ARITHMETIC:
                result_type = (
                    "float"
                    if "float" in (left_type, right_type)
                    else "int"
                )

                if operator == "/":
                    result_type = "float"

                if operator == "//":
                    opcode = (
                        "FLOOR_DIV_FLOAT"
                        if result_type == "float"
                        else "FLOOR_DIV_INT"
                    )
                elif operator == "%":
                    opcode = (
                        "MOD_FLOAT"
                        if result_type == "float"
                        else "MOD_INT"
                    )
                elif operator == "**":
                    opcode = (
                        "POWER_FLOAT"
                        if result_type == "float"
                        else "POWER_INT"
                    )
                else:
                    int_opcode, float_opcode = self.ARITHMETIC[operator]
                    opcode = (
                        float_opcode if result_type == "float"
                        else int_opcode
                    )

                self.emit(opcode)
                return result_type

        raise IntermediateCodeError(
            f"Unsupported expression: {type(node).__name__}"
        )

    def compile_logical(self, node):
        operator = node.operator

        end_label = self.new_label()
        short_label = self.new_label()

        self.compile_expression(node.left)
        self.emit("TO_BOOL")

        if operator == "and":
            self.emit("JUMP_IF_FALSE", short_label)
            self.compile_expression(node.right)
            self.emit("TO_BOOL")
            self.emit("JUMP", end_label)
            self.mark_label(short_label)
            self.emit("LOAD_BOOL", False)

        else:
            self.emit("JUMP_IF_TRUE", short_label)
            self.compile_expression(node.right)
            self.emit("TO_BOOL")
            self.emit("JUMP", end_label)
            self.mark_label(short_label)
            self.emit("LOAD_BOOL", True)

        self.mark_label(end_label)
        return "bool"


class IntermediateCodeLowerer:
    """
    Converts symbolic IR instructions into executable bytecode.

    The BytecodeProgram uses:
      - 8-bit opcode
      - 16-bit operand
      - Separate typed constant pool
      - Separate variable-name table
    """

    def __init__(self):
        self.program = BytecodeProgram()

    def lower(self, ir_instructions):
        self.program = BytecodeProgram()

        labels = {}
        pending_jumps = []

        # First pass: emit instructions and record labels.
        for instruction in ir_instructions:
            op = instruction.opcode
            arg = instruction.operand

            if op == "LABEL":
                labels[arg] = len(self.program.instructions)
                continue

            if op == "LOAD_INT":
                index = self.program.add_constant(int(arg))
                self.program.add_instruction(Opcode.LOAD_INT, index)

            elif op == "LOAD_FLOAT":
                index = self.program.add_constant(float(arg))
                self.program.add_instruction(Opcode.LOAD_FLOAT, index)

            elif op == "LOAD_BOOL":
                index = self.program.add_constant(bool(arg))
                self.program.add_instruction(Opcode.LOAD_BOOL, index)

            elif op == "LOAD_VAR":
                index = self.program.add_name(arg)
                self.program.add_instruction(Opcode.LOAD_VAR, index)

            elif op == "STORE_VAR":
                index = self.program.add_name(arg)
                self.program.add_instruction(Opcode.STORE_VAR, index)

            elif op in ("JUMP", "JUMP_IF_FALSE", "JUMP_IF_TRUE"):
                bytecode_opcode = Opcode[op]
                instruction_index = len(self.program.instructions)

                self.program.add_instruction(bytecode_opcode, 0)
                pending_jumps.append((instruction_index, arg))

            else:
                self.program.add_instruction(Opcode[op])

        # Second pass: resolve jump destinations.
        for instruction_index, label in pending_jumps:
            if label not in labels:
                raise IntermediateCodeError(
                    f"Undefined jump label: {label}"
                )

            target = labels[label]

            if target > 65535:
                raise IntermediateCodeError(
                    "Bytecode program exceeds jump address limit"
                )

            self.program.instructions[instruction_index].operand = target

        return self.program


def generate_intermediate_code(ast):
    generator = IntermediateCodeGenerator()
    return generator.compile(ast)


def generate_bytecode(ast):
    ir = generate_intermediate_code(ast)
    lowerer = IntermediateCodeLowerer()
    return lowerer.lower(ir)
