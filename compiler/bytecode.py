
# compiler/bytecode.py

from dataclasses import dataclass, field
from enum import IntEnum
import struct


class Opcode(IntEnum):

    # Program control
    HALT = 0x00
    POP = 0x01

    # Loading and storing
    LOAD_INT = 0x02
    LOAD_FLOAT = 0x03
    LOAD_BOOL = 0x04
    LOAD_VAR = 0x05
    STORE_VAR = 0x06

    # Integer arithmetic
    ADD_INT = 0x10
    SUB_INT = 0x11
    MUL_INT = 0x12
    DIV_INT = 0x13
    FLOOR_DIV_INT = 0x14
    MOD_INT = 0x15
    POWER_INT = 0x16

    # Floating-point arithmetic
    ADD_FLOAT = 0x20
    SUB_FLOAT = 0x21
    MUL_FLOAT = 0x22
    DIV_FLOAT = 0x23
    FLOOR_DIV_FLOAT = 0x24
    MOD_FLOAT = 0x25
    POWER_FLOAT = 0x26

    # Comparisons
    CMP_EQ = 0x30
    CMP_NE = 0x31
    CMP_LT = 0x32
    CMP_GT = 0x33
    CMP_LE = 0x34
    CMP_GE = 0x35

    # Logical operations
    TO_BOOL = 0x40
    LOGICAL_AND = 0x41
    LOGICAL_OR = 0x42
    LOGICAL_NOT = 0x43

    # Bitwise operations
    BIT_AND = 0x50
    BIT_OR = 0x51
    BIT_XOR = 0x52
    BIT_NOT = 0x53

    # Shift operations
    LSHIFT = 0x54
    RSHIFT = 0x55

    # Unary operations
    NEG = 0x60
    POS = 0x61

    # Type conversion
    INT_TO_FLOAT = 0x70
    FLOAT_TO_INT = 0x71

    # Conditional jumps
    JUMP = 0x80
    JUMP_IF_FALSE = 0x81
    JUMP_IF_TRUE = 0x82

    # Output
    PRINT_INT = 0x90
    PRINT_FLOAT = 0x91
    PRINT_BOOL = 0x92


@dataclass
class Instruction:
    opcode: Opcode
    operand: int = 0

    def __post_init__(self):
        self.opcode = Opcode(self.opcode)

        if not isinstance(self.operand, int):
            raise TypeError("Instruction operand must be an integer")

        if not 0 <= self.operand <= 65535:
            raise ValueError("Operand must fit in 16 bits")

    def encode(self):
        """
        24-bit instruction:
        8-bit opcode + 16-bit operand.
        """
        return struct.pack(
            ">BH",
            int(self.opcode),
            self.operand
        )

    @classmethod
    def decode(cls, data):
        if len(data) != 3:
            raise ValueError(
                "Each instruction must contain exactly 3 bytes"
            )

        opcode, operand = struct.unpack(">BH", data)

        return cls(
            opcode=Opcode(opcode),
            operand=operand
        )


@dataclass
class Constant:
    value: object
    data_type: str

    def encode(self):
        if self.data_type == "int":
            return b"I" + struct.pack(">q", self.value)

        if self.data_type == "float":
            return b"F" + struct.pack(">d", self.value)

        if self.data_type == "bool":
            return b"B" + bytes([1 if self.value else 0])

        raise ValueError(
            f"Unsupported constant type: {self.data_type}"
        )


@dataclass
class BytecodeProgram:

    instructions: list = field(default_factory=list)
    constants: list = field(default_factory=list)
    names: list = field(default_factory=list)

    def add_instruction(self, opcode, operand=0):
        instruction = Instruction(
            Opcode(opcode),
            operand
        )

        self.instructions.append(instruction)

        return len(self.instructions) - 1

    def add_constant(self, value):

        if isinstance(value, bool):
            constant = Constant(value, "bool")

        elif isinstance(value, int):
            constant = Constant(value, "int")

        elif isinstance(value, float):
            constant = Constant(value, "float")

        else:
            raise TypeError(
                f"Unsupported constant type: {type(value).__name__}"
            )

        if len(self.constants) >= 65536:
            raise ValueError("Constant pool limit exceeded")

        self.constants.append(constant)

        return len(self.constants) - 1

    def add_name(self, name):
        if not isinstance(name, str):
            raise TypeError("Variable name must be a string")

        if name not in self.names:
            if len(self.names) >= 65536:
                raise ValueError("Name table limit exceeded")

            self.names.append(name)

        return self.names.index(name)

    def get_constant(self, index):
        if not 0 <= index < len(self.constants):
            raise IndexError("Invalid constant index")

        return self.constants[index]

    def get_name(self, index):
        if not 0 <= index < len(self.names):
            raise IndexError("Invalid variable name index")

        return self.names[index]

    def serialize(self):
        return b"".join(
            instruction.encode()
            for instruction in self.instructions
        )

    @staticmethod
    def deserialize(binary):
        if len(binary) % 3 != 0:
            raise ValueError(
                "Invalid bytecode: length must be divisible by 3"
            )

        program = BytecodeProgram()

        for position in range(0, len(binary), 3):
            chunk = binary[position:position + 3]
            program.instructions.append(
                Instruction.decode(chunk)
            )

        return program

    def dump(self):
        print("\nBYTECODE")
        print("-" * 55)

        for index, instruction in enumerate(self.instructions):
            print(
                f"{index:04d} | "
                f"{instruction.opcode.name:<20} | "
                f"{instruction.operand:05d}"
            )

        print("\nCONSTANT POOL")
        print("-" * 55)

        for index, constant in enumerate(self.constants):
            print(
                f"{index:04d} | "
                f"{constant.data_type:<8} | "
                f"{constant.value!r}"
            )

        print("\nVARIABLE TABLE")
        print("-" * 55)

        for index, name in enumerate(self.names):
            print(f"{index:04d} | {name}")

    def save(self, filename):
        with open(filename, "wb") as file:
            file.write(self.serialize())

    @staticmethod
    def load(filename):
        with open(filename, "rb") as file:
            binary = file.read()

        return BytecodeProgram.deserialize(binary)


def encode_instruction(opcode, operand=0):
    return Instruction(opcode, operand).encode()


def decode_instruction(data):
    return Instruction.decode(data)
