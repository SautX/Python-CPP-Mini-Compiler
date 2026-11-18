
import unittest

from compiler.bytecode import Instruction


class TestBytecode(unittest.TestCase):

    def test_instruction_encoding(self):

        instruction = Instruction(
            opcode=1,
            operand=10
        )

        encoded = instruction.encode()

        self.assertEqual(
            encoded,
            (1 << 16) | 10
        )

    def test_instruction_size(self):

        instruction = Instruction(
            opcode=1,
            operand=10
        )

        encoded = instruction.encode()

        self.assertLessEqual(encoded, 0xFFFFFF)

    def test_opcode_range(self):

        instruction = Instruction(
            opcode=1,
            operand=100
        )

        self.assertGreaterEqual(instruction.opcode, 0)
        self.assertLessEqual(instruction.opcode, 255)

    def test_operand_range(self):

        instruction = Instruction(
            opcode=1,
            operand=100
        )

        self.assertGreaterEqual(instruction.operand, 0)
        self.assertLessEqual(instruction.operand, 65535)


if __name__ == "__main__":
    unittest.main()
