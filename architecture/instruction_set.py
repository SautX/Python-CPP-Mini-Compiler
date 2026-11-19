
from enum import IntEnum
from dataclasses import dataclass


class Opcode(IntEnum):
    HALT = 0x00
    POP = 0x01

    LOAD_INT = 0x02
    LOAD_FLOAT = 0x03
    LOAD_BOOL = 0x04
    LOAD_VAR = 0x05
    STORE_VAR = 0x06

    ADD_INT = 0x10
    SUB_INT = 0x11
    MUL_INT = 0x12
    DIV_INT = 0x13
    FLOOR_DIV_INT = 0x14
    MOD_INT = 0x15
    POWER_INT = 0x16

    ADD_FLOAT = 0x20
    SUB_FLOAT = 0x21
    MUL_FLOAT = 0x22
    DIV_FLOAT = 0x23
    FLOOR_DIV_FLOAT = 0x24
    MOD_FLOAT = 0x25
    POWER_FLOAT = 0x26

    CMP_EQ = 0x30
    CMP_NE = 0x31
    CMP_LT = 0x32
    CMP_GT = 0x33
    CMP_LE = 0x34
    CMP_GE = 0x35

    TO_BOOL = 0x40
    LOGICAL_AND = 0x41
    LOGICAL_OR = 0x42
    LOGICAL_NOT = 0x43

    BIT_AND = 0x50
    BIT_OR = 0x51
    BIT_XOR = 0x52
    BIT_NOT = 0x53
    LSHIFT = 0x54
    RSHIFT = 0x55

    NEG = 0x60
    POS = 0x61

    INT_TO_FLOAT = 0x70
    FLOAT_TO_INT = 0x71

    JUMP = 0x80
    JUMP_IF_FALSE = 0x81
    JUMP_IF_TRUE = 0x82

    PRINT_INT = 0x90
    PRINT_FLOAT = 0x91
    PRINT_BOOL = 0x92


@dataclass
class MachineInstruction:
    opcode: Opcode
    operand: int = 0

    def __post_init__(self):
        self.opcode = Opcode(self.opcode)

        if not isinstance(self.operand, int):
            raise TypeError("Instruction operand must be an integer.")

        if not 0 <= self.operand <= 0xFFFF:
            raise ValueError("Operand must fit in 16 bits.")

    def encode(self) -> bytes:
        return self.opcode.to_bytes(1, "big") + self.operand.to_bytes(2, "big")

    @classmethod
    def decode(cls, data: bytes):
        if len(data) != 3:
            raise ValueError("An instruction must contain exactly 3 bytes.")

        opcode = Opcode(data[0])
        operand = int.from_bytes(data[1:3], "big")

        return cls(opcode, operand)

    def __str__(self):
        return f"{self.opcode.name:<16} {self.operand:5d}"


INSTRUCTION_SIZE = 3
OPCODE_SIZE = 1
OPERAND_SIZE = 2
