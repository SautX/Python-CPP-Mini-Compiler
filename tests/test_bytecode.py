
import unittest

from compiler.bytecode import (
    Instruction,
    Constant,
    BytecodeProgram
)


class TestBytecode(unittest.TestCase):

    def test_instruction_encoding(self):
        instruction = Instruction(0x10, 25)

        encoded = instruction.encode()

        self.assertEqual(len(encoded), 3)
        self.assertEqual(encoded[0], 0x10)
        self.assertEqual(int.from_bytes(encoded[1:], "big"), 25)

    def test_instruction_decoding(self):
        instruction = Instruction(0x10, 25)

        encoded = instruction.encode()
        decoded = Instruction.decode(encoded)

        self.assertEqual(decoded.opcode, instruction.opcode)
        self.assertEqual(decoded.operand, instruction.operand)

    def test_constant_pool_integer(self):
        program = BytecodeProgram()

        index = program.add_constant(100, "int")

        constant = program.get_constant(index)

        self.assertEqual(constant.value, 100)

    def test_constant_pool_float(self):
        program = BytecodeProgram()

        index = program.add_constant(10.5, "float")

        constant = program.get_constant(index)

        self.assertAlmostEqual(constant.value, 10.5)

    def test_constant_pool_boolean(self):
        program = BytecodeProgram()

        index = program.add_constant(True, "bool")

        constant = program.get_constant(index)

        self.assertEqual(constant.value, True)

    def test_variable_name_table(self):
        program = BytecodeProgram()

        index = program.add_name("total")

        self.assertEqual(program.get_name(index), "total")

    def test_add_instruction(self):
        program = BytecodeProgram()

        program.add_instruction(0x00, 0)

        self.assertEqual(len(program.instructions), 1)

    def test_bytecode_dump(self):
        program = BytecodeProgram()

        program.add_constant(10, "int")
        program.add_instruction(0x02, 0)
        program.add_instruction(0x00, 0)

        dump = program.dump()

        self.assertIsNotNone(dump)


if __name__ == "__main__":
    unittest.main()
