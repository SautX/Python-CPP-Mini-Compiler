
from dataclasses import dataclass


# ==========================================
# 24-BIT PROCESSOR INSTRUCTION SET
# ==========================================

OPCODES = {
    "NOP":        0x00,
    "LOAD_CONST": 0x01,
    "STORE_VAR":  0x02,
    "LOAD_VAR":   0x03,

    "ADD":        0x04,
    "SUB":        0x05,
    "MUL":        0x06,
    "DIV":        0x07,
    "MOD":        0x08,

    "PRINT":      0x09,
    "HALT":       0x0A,
    "NEG":        0x0B,

    "AND":        0x0C,
    "OR":         0x0D,
    "XOR":        0x0E,
    "NOT":        0x0F,

    "SHL":        0x10,
    "SHR":        0x11,

    "CMP":        0x12,
    "JMP":        0x13,
    "JZ":         0x14,
    "JNZ":        0x15
}


REVERSE_OPCODES = {
    value: key
    for key, value in OPCODES.items()
}


@dataclass
class Instruction:

    opcode: str
    operand: int = 0

    def __post_init__(self):

        if self.opcode not in OPCODES:
            raise ValueError(
                f"Invalid opcode: {self.opcode}"
            )

        if not 0 <= self.operand <= 0xFFFF:
            raise ValueError(
                "Operand must be between 0 and 65535"
            )

    def encode(self):

        return (
            (OPCODES[self.opcode] << 16)
            | self.operand
        )

    def to_bytes(self):

        return self.encode().to_bytes(
            3,
            byteorder="big"
        )

    def to_binary(self):

        return f"{self.encode():024b}"

    def to_hex(self):

        return f"0x{self.encode():06X}"

    @classmethod
    def decode(cls, value):

        opcode_value = (value >> 16) & 0xFF
        operand = value & 0xFFFF

        if opcode_value not in REVERSE_OPCODES:
            raise ValueError("Unknown opcode")

        return cls(
            REVERSE_OPCODES[opcode_value],
            operand
        )


def decode_bytes(data):

    if len(data) != 3:
        raise ValueError(
            "A 24-bit instruction requires 3 bytes"
        )

    value = int.from_bytes(data, "big")

    return Instruction.decode(value)
