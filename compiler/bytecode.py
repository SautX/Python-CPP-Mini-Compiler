from dataclasses import dataclass, field


OPCODES = {
    "LOAD_CONST": 0x01,
    "STORE_VAR": 0x02,
    "LOAD_VAR": 0x03,
    "ADD": 0x04,
    "SUB": 0x05,
    "MUL": 0x06,
    "DIV": 0x07,
    "MOD": 0x08,
    "PRINT": 0x09,
    "HALT": 0x0A,
    "NEG": 0x0B
}

REVERSE_OPCODES = {
    value: key
    for key, value in OPCODES.items()
}


@dataclass
class Instruction:

    opcode: str
    operand: int = 0

    def encode(self):

        if self.opcode not in OPCODES:
            raise ValueError("Invalid opcode")

        if not 0 <= self.operand <= 65535:
            raise ValueError("Operand must fit in 16 bits")

        return (
            (OPCODES[self.opcode] << 16)
            | self.operand
        )

    def bits(self):

        return f"{self.encode():024b}"

    def hex(self):

        return f"0x{self.encode():06X}"


@dataclass
class Program:

    instructions: list = field(default_factory=list)
    constants: list = field(default_factory=list)
    variables: list = field(default_factory=list)


def format_program(program):

    lines = [
        "PC | INSTRUCTION | OPCODE | OPERAND | 24-BIT HEX"
    ]

    for pc, instruction in enumerate(program.instructions):

        lines.append(
            f"{pc} | {instruction.opcode} | "
            f"0x{OPCODES[instruction.opcode]:02X} | "
            f"0x{instruction.operand:04X} | "
            f"{instruction.hex()}"
        )

    return "\n".join(lines)