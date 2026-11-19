
# compiler/optimizer.py

from .bytecode import BytecodeProgram, Opcode, Instruction


class OptimizationError(Exception):
    pass


class BytecodeOptimizer:

    INTEGER_OPS = {
        Opcode.ADD_INT,
        Opcode.SUB_INT,
        Opcode.MUL_INT,
        Opcode.DIV_INT,
        Opcode.FLOOR_DIV_INT,
        Opcode.MOD_INT,
        Opcode.POWER_INT,
    }

    FLOAT_OPS = {
        Opcode.ADD_FLOAT,
        Opcode.SUB_FLOAT,
        Opcode.MUL_FLOAT,
        Opcode.DIV_FLOAT,
        Opcode.FLOOR_DIV_FLOAT,
        Opcode.MOD_FLOAT,
        Opcode.POWER_FLOAT,
    }

    COMPARISON_OPS = {
        Opcode.CMP_EQ,
        Opcode.CMP_NE,
        Opcode.CMP_LT,
        Opcode.CMP_GT,
        Opcode.CMP_LE,
        Opcode.CMP_GE,
    }

    JUMP_OPS = {
        Opcode.JUMP,
        Opcode.JUMP_IF_FALSE,
        Opcode.JUMP_IF_TRUE,
    }

    def __init__(self, program):
        if not isinstance(program, BytecodeProgram):
            raise TypeError("Expected BytecodeProgram")

        self.program = program

    @staticmethod
    def _calculate(opcode, a, b):
        if opcode in (Opcode.ADD_INT, Opcode.ADD_FLOAT):
            return a + b

        if opcode in (Opcode.SUB_INT, Opcode.SUB_FLOAT):
            return a - b

        if opcode in (Opcode.MUL_INT, Opcode.MUL_FLOAT):
            return a * b

        if opcode in (Opcode.DIV_INT, Opcode.DIV_FLOAT):
            if b == 0:
                raise ZeroDivisionError
            return a / b

        if opcode in (
            Opcode.FLOOR_DIV_INT,
            Opcode.FLOOR_DIV_FLOAT
        ):
            if b == 0:
                raise ZeroDivisionError
            return a // b

        if opcode in (Opcode.MOD_INT, Opcode.MOD_FLOAT):
            if b == 0:
                raise ZeroDivisionError
            return a % b

        if opcode in (Opcode.POWER_INT, Opcode.POWER_FLOAT):
            return a ** b

        if opcode == Opcode.CMP_EQ:
            return a == b
        if opcode == Opcode.CMP_NE:
            return a != b
        if opcode == Opcode.CMP_LT:
            return a < b
        if opcode == Opcode.CMP_GT:
            return a > b
        if opcode == Opcode.CMP_LE:
            return a <= b
        if opcode == Opcode.CMP_GE:
            return a >= b

        raise OptimizationError(
            f"Unsupported constant operation: {opcode.name}"
        )

    def _is_numeric(self, value):
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
        )

    def _fold_instruction(self, first, second, operation):
        load_ops = {
            Opcode.LOAD_INT,
            Opcode.LOAD_FLOAT,
            Opcode.LOAD_BOOL,
        }

        if first.opcode not in load_ops:
            return None

        if second.opcode not in load_ops:
            return None

        supported = self.INTEGER_OPS | self.FLOAT_OPS | self.COMPARISON_OPS

        if operation.opcode not in supported:
            return None

        a = self.program.get_constant(first.operand).value
        b = self.program.get_constant(second.operand).value

        if not self._is_numeric(a) or not self._is_numeric(b):
            if operation.opcode not in (
                Opcode.CMP_EQ, Opcode.CMP_NE
            ):
                return None

        try:
            result = self._calculate(operation.opcode, a, b)
        except (ArithmeticError, ValueError, OverflowError):
            # Keep the original instructions. Runtime must report the error.
            return None

        if isinstance(result, bool):
            new_opcode = Opcode.LOAD_BOOL
        elif isinstance(result, float):
            new_opcode = Opcode.LOAD_FLOAT
        elif isinstance(result, int):
            new_opcode = Opcode.LOAD_INT
        else:
            return None

        constant_index = self.program.add_constant(result)

        return Instruction(new_opcode, constant_index)

    def validate(self):
        for instruction in self.program.instructions:
            if not isinstance(instruction, Instruction):
                raise OptimizationError(
                    "Program contains an invalid instruction"
                )

            if instruction.opcode in (
                Opcode.LOAD_INT,
                Opcode.LOAD_FLOAT,
                Opcode.LOAD_BOOL,
            ):
                constant = self.program.get_constant(
                    instruction.operand
                )

                expected = {
                    Opcode.LOAD_INT: "int",
                    Opcode.LOAD_FLOAT: "float",
                    Opcode.LOAD_BOOL: "bool",
                }[instruction.opcode]

                if constant.data_type != expected:
                    raise OptimizationError(
                        f"{instruction.opcode.name} references "
                        f"a {constant.data_type} constant"
                    )

            if instruction.opcode in (
                Opcode.LOAD_VAR,
                Opcode.STORE_VAR,
            ):
                self.program.get_name(instruction.operand)

            if instruction.opcode in self.JUMP_OPS:
                if not (
                    0 <= instruction.operand
                    < len(self.program.instructions)
                ):
                    raise OptimizationError(
                        f"Invalid jump target: {instruction.operand}"
                    )

        return True

    def optimize(self):
        self.validate()

        instructions = self.program.instructions

        # Replacing instructions changes absolute jump destinations.
        # Therefore, retain the original stream when jumps are present.
        if any(
            instruction.opcode in self.JUMP_OPS
            for instruction in instructions
        ):
            return self.program

        optimized = []
        index = 0

        while index < len(instructions):

            if index + 2 < len(instructions):
                folded = self._fold_instruction(
                    instructions[index],
                    instructions[index + 1],
                    instructions[index + 2],
                )

                if folded is not None:
                    optimized.append(folded)
                    index += 3
                    continue

            optimized.append(instructions[index])
            index += 1

        self.program.instructions = optimized

        self.validate()
        return self.program


def optimize_bytecode(program):
    return BytecodeOptimizer(program).optimize()
