from .bytecode import Instruction


BINARY_OPERATIONS = {
    "ADD": lambda a, b: a + b,
    "SUB": lambda a, b: a - b,
    "MUL": lambda a, b: a * b,
    "DIV": lambda a, b: a // b,
    "MOD": lambda a, b: a % b
}


def optimize_program(program):

    instructions = program.instructions
    constants = program.constants

    optimized = []
    i = 0

    while i < len(instructions):

        if i + 2 < len(instructions):

            first = instructions[i]
            second = instructions[i + 1]
            third = instructions[i + 2]

            if (
                first.opcode == "LOAD_CONST"
                and second.opcode == "LOAD_CONST"
                and third.opcode in BINARY_OPERATIONS
            ):

                a = constants[first.operand]
                b = constants[second.operand]

                operation = BINARY_OPERATIONS[
                    third.opcode
                ]

                if not (
                    third.opcode in ("DIV", "MOD")
                    and b == 0
                ):

                    result = operation(a, b)

                    if result not in constants:
                        constants.append(result)

                    index = constants.index(result)

                    optimized.append(
                        Instruction("LOAD_CONST", index)
                    )

                    i += 3
                    continue

        optimized.append(instructions[i])
        i += 1

    program.instructions = optimized

    return program