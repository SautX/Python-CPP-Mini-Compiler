
# compiler/bytecode_decoder.py

from .bytecode import BytecodeProgram, Opcode


class BytecodeExecutionError(Exception):
    pass


class BytecodeDecoder:

    def __init__(self, program):
        if not isinstance(program, BytecodeProgram):
            raise TypeError("Expected BytecodeProgram")

        self.program = program
        self.stack = []
        self.variables = {}
        self.pc = 0

    def reset(self):
        self.stack = []
        self.variables = {}
        self.pc = 0

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        if not self.stack:
            raise BytecodeExecutionError(
                "Stack underflow"
            )

        return self.stack.pop()

    def pop_two(self):
        right = self.pop()
        left = self.pop()

        return left, right

    @staticmethod
    def is_number(value):
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
        )

    @staticmethod
    def is_integer(value):
        return (
            isinstance(value, int)
            and not isinstance(value, bool)
        )

    def require_integer_operands(self, a, b):
        if not self.is_integer(a) or not self.is_integer(b):
            raise BytecodeExecutionError(
                "Bitwise and shift operations require integers"
            )

    def arithmetic(self, opcode, a, b):

        if not self.is_number(a) or not self.is_number(b):
            raise BytecodeExecutionError(
                "Arithmetic requires numeric operands"
            )

        try:

            if opcode in (
                Opcode.ADD_INT,
                Opcode.ADD_FLOAT
            ):
                return a + b

            if opcode in (
                Opcode.SUB_INT,
                Opcode.SUB_FLOAT
            ):
                return a - b

            if opcode in (
                Opcode.MUL_INT,
                Opcode.MUL_FLOAT
            ):
                return a * b

            if opcode in (
                Opcode.DIV_INT,
                Opcode.DIV_FLOAT
            ):
                if b == 0:
                    raise ZeroDivisionError(
                        "Division by zero"
                    )

                # Python-style true division.
                return a / b

            if opcode in (
                Opcode.FLOOR_DIV_INT,
                Opcode.FLOOR_DIV_FLOAT
            ):
                if b == 0:
                    raise ZeroDivisionError(
                        "Floor division by zero"
                    )

                return a // b

            if opcode in (
                Opcode.MOD_INT,
                Opcode.MOD_FLOAT
            ):
                if b == 0:
                    raise ZeroDivisionError(
                        "Modulo by zero"
                    )

                return a % b

            if opcode in (
                Opcode.POWER_INT,
                Opcode.POWER_FLOAT
            ):
                return a ** b

        except ZeroDivisionError:
            raise

        except (OverflowError, ValueError) as error:
            raise BytecodeExecutionError(
                f"Arithmetic error: {error}"
            ) from error

        raise BytecodeExecutionError(
            f"Unsupported arithmetic opcode: {opcode}"
        )

    def comparison(self, opcode, a, b):

        operations = {
            Opcode.CMP_EQ: lambda x, y: x == y,
            Opcode.CMP_NE: lambda x, y: x != y,
            Opcode.CMP_LT: lambda x, y: x < y,
            Opcode.CMP_GT: lambda x, y: x > y,
            Opcode.CMP_LE: lambda x, y: x <= y,
            Opcode.CMP_GE: lambda x, y: x >= y,
        }

        if opcode not in operations:
            raise BytecodeExecutionError(
                f"Unsupported comparison opcode: {opcode}"
            )

        try:
            return bool(operations[opcode](a, b))

        except TypeError as error:
            raise BytecodeExecutionError(
                f"Invalid comparison: {error}"
            ) from error

    def logical(self, opcode, a, b):

        if opcode == Opcode.LOGICAL_AND:
            return bool(a) and bool(b)

        if opcode == Opcode.LOGICAL_OR:
            return bool(a) or bool(b)

        raise BytecodeExecutionError(
            f"Unsupported logical opcode: {opcode}"
        )

    def bitwise(self, opcode, a, b=None):

        if opcode == Opcode.BIT_NOT:
            if not self.is_integer(a):
                raise BytecodeExecutionError(
                    "Bitwise NOT requires an integer"
                )
            return ~a

        self.require_integer_operands(a, b)

        if opcode == Opcode.BIT_AND:
            return a & b

        if opcode == Opcode.BIT_OR:
            return a | b

        if opcode == Opcode.BIT_XOR:
            return a ^ b

        if opcode == Opcode.LSHIFT:
            if b < 0:
                raise ValueError(
                    "Negative shift count"
                )
            return a << b

        if opcode == Opcode.RSHIFT:
            if b < 0:
                raise ValueError(
                    "Negative shift count"
                )
            return a >> b

        raise BytecodeExecutionError(
            f"Unsupported bitwise opcode: {opcode}"
        )

    def execute_instruction(self, instruction):

        opcode = instruction.opcode
        operand = instruction.operand

        # ---------------------------------
        # PROGRAM CONTROL
        # ---------------------------------

        if opcode == Opcode.HALT:
            return False

        if opcode == Opcode.POP:
            self.pop()
            return True

        # ---------------------------------
        # CONSTANT LOADING
        # ---------------------------------

        if opcode in (
            Opcode.LOAD_INT,
            Opcode.LOAD_FLOAT,
            Opcode.LOAD_BOOL
        ):
            constant = self.program.get_constant(operand)

            expected_type = {
                Opcode.LOAD_INT: "int",
                Opcode.LOAD_FLOAT: "float",
                Opcode.LOAD_BOOL: "bool"
            }[opcode]

            if constant.data_type != expected_type:
                raise BytecodeExecutionError(
                    f"Expected {expected_type} constant, "
                    f"got {constant.data_type}"
                )

            self.push(constant.value)
            return True

        # ---------------------------------
        # VARIABLE OPERATIONS
        # ---------------------------------

        if opcode == Opcode.STORE_VAR:
            name = self.program.get_name(operand)
            value = self.pop()

            self.variables[name] = value
            return True

        if opcode == Opcode.LOAD_VAR:
            name = self.program.get_name(operand)

            if name not in self.variables:
                raise BytecodeExecutionError(
                    f"Undefined variable: {name}"
                )

            self.push(self.variables[name])
            return True

        # ---------------------------------
        # ARITHMETIC OPERATIONS
        # ---------------------------------

        arithmetic_opcodes = {
            Opcode.ADD_INT,
            Opcode.SUB_INT,
            Opcode.MUL_INT,
            Opcode.DIV_INT,
            Opcode.FLOOR_DIV_INT,
            Opcode.MOD_INT,
            Opcode.POWER_INT,

            Opcode.ADD_FLOAT,
            Opcode.SUB_FLOAT,
            Opcode.MUL_FLOAT,
            Opcode.DIV_FLOAT,
            Opcode.FLOOR_DIV_FLOAT,
            Opcode.MOD_FLOAT,
            Opcode.POWER_FLOAT
        }

        if opcode in arithmetic_opcodes:
            a, b = self.pop_two()

            self.push(
                self.arithmetic(opcode, a, b)
            )

            return True

        # ---------------------------------
        # COMPARISON OPERATIONS
        # ---------------------------------

        comparison_opcodes = {
            Opcode.CMP_EQ,
            Opcode.CMP_NE,
            Opcode.CMP_LT,
            Opcode.CMP_GT,
            Opcode.CMP_LE,
            Opcode.CMP_GE
        }

        if opcode in comparison_opcodes:
            a, b = self.pop_two()

            self.push(
                self.comparison(opcode, a, b)
            )

            return True

        # ---------------------------------
        # LOGICAL OPERATIONS
        # ---------------------------------

        if opcode == Opcode.TO_BOOL:
            self.push(bool(self.pop()))
            return True

        if opcode == Opcode.LOGICAL_NOT:
            self.push(not bool(self.pop()))
            return True

        if opcode in (
            Opcode.LOGICAL_AND,
            Opcode.LOGICAL_OR
        ):
            a, b = self.pop_two()

            self.push(
                self.logical(opcode, a, b)
            )

            return True

        # ---------------------------------
        # BITWISE OPERATIONS
        # ---------------------------------

        if opcode == Opcode.BIT_NOT:
            self.push(
                self.bitwise(opcode, self.pop())
            )
            return True

        if opcode in (
            Opcode.BIT_AND,
            Opcode.BIT_OR,
            Opcode.BIT_XOR,
            Opcode.LSHIFT,
            Opcode.RSHIFT
        ):
            a, b = self.pop_two()

            self.push(
                self.bitwise(opcode, a, b)
            )

            return True

        # ---------------------------------
        # UNARY OPERATIONS
        # ---------------------------------

        if opcode == Opcode.NEG:
            value = self.pop()

            if not self.is_number(value):
                raise BytecodeExecutionError(
                    "Unary minus requires a numeric value"
                )

            self.push(-value)
            return True

        if opcode == Opcode.POS:
            value = self.pop()

            if not self.is_number(value):
                raise BytecodeExecutionError(
                    "Unary plus requires a numeric value"
                )

            self.push(+value)
            return True

        # ---------------------------------
        # TYPE CONVERSIONS
        # ---------------------------------

        if opcode == Opcode.INT_TO_FLOAT:
            value = self.pop()

            if not self.is_integer(value):
                raise BytecodeExecutionError(
                    "INT_TO_FLOAT requires an integer"
                )

            self.push(float(value))
            return True

        if opcode == Opcode.FLOAT_TO_INT:
            value = self.pop()

            if not isinstance(value, float):
                raise BytecodeExecutionError(
                    "FLOAT_TO_INT requires a float"
                )

            self.push(int(value))
            return True

        # ---------------------------------
        # CONDITIONAL JUMPS
        # ---------------------------------

        if opcode == Opcode.JUMP:
            self.check_jump(operand)
            self.pc = operand
            return True

        if opcode == Opcode.JUMP_IF_FALSE:
            condition = bool(self.pop())

            if not condition:
                self.check_jump(operand)
                self.pc = operand

            return True

        if opcode == Opcode.JUMP_IF_TRUE:
            condition = bool(self.pop())

            if condition:
                self.check_jump(operand)
                self.pc = operand

            return True

        # ---------------------------------
        # PRINT OPERATIONS
        # ---------------------------------

        if opcode == Opcode.PRINT_INT:
            value = self.pop()

            if not self.is_integer(value):
                raise BytecodeExecutionError(
                    "PRINT_INT requires an integer"
                )

            print(value)
            return True

        if opcode == Opcode.PRINT_FLOAT:
            value = self.pop()

            if not isinstance(value, float):
                raise BytecodeExecutionError(
                    "PRINT_FLOAT requires a float"
                )

            print(value)
            return True

        if opcode == Opcode.PRINT_BOOL:
            value = self.pop()

            if not isinstance(value, bool):
                raise BytecodeExecutionError(
                    "PRINT_BOOL requires a Boolean"
                )

            print(value)
            return True

        raise BytecodeExecutionError(
            f"Unknown opcode: {opcode}"
        )

    def check_jump(self, target):
        if not 0 <= target < len(self.program.instructions):
            raise BytecodeExecutionError(
                f"Invalid jump target: {target}"
            )

    def execute(self):

        self.reset()

        instructions = self.program.instructions

        while self.pc < len(instructions):

            instruction = instructions[self.pc]
            self.pc += 1

            try:
                should_continue = self.execute_instruction(
                    instruction
                )

            except Exception as error:
                raise BytecodeExecutionError(
                    f"Error at instruction {self.pc - 1} "
                    f"({instruction.opcode.name}): {error}"
                ) from error

            if not should_continue:
                break

        return {
            "variables": self.variables.copy(),
            "stack": self.stack.copy()
        }


def execute_bytecode(program):
    decoder = BytecodeDecoder(program)
    return decoder.execute()
