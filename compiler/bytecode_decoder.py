from .bytecode import (
    Instruction,
    OPCODES,
    REVERSE_OPCODES
)


def encode_instruction(instruction):

    value = instruction.encode()

    return value.to_bytes(
        3,
        byteorder="big"
    )


def encode_program(program):

    binary_data = bytearray()

    for instruction in program.instructions:

        binary_data.extend(
            encode_instruction(instruction)
        )

    return bytes(binary_data)


def decode_instruction(data):

    if len(data) != 3:

        raise ValueError(
            "Instruction must contain exactly 3 bytes"
        )

    value = int.from_bytes(
        data,
        byteorder="big"
    )

    opcode_value = (value >> 16) & 0xFF
    operand = value & 0xFFFF

    if opcode_value not in REVERSE_OPCODES:

        raise ValueError("Unknown opcode")

    return Instruction(
        REVERSE_OPCODES[opcode_value],
        operand
    )


def decode_program(binary_data):

    if len(binary_data) % 3 != 0:

        raise ValueError(
            "Invalid bytecode length"
        )

    instructions = []

    for i in range(0, len(binary_data), 3):

        instructions.append(
            decode_instruction(
                binary_data[i:i + 3]
            )
        )

    return instructions