
import unittest

from compiler.frontend import Frontend
from compiler.intermediate_code import (
    IntermediateCodeGenerator,
    IntermediateCodeLowerer
)


class TestIntermediateCodeLowering(unittest.TestCase):

    def setUp(self):
        self.frontend = Frontend()
        self.generator = IntermediateCodeGenerator()
        self.lowerer = IntermediateCodeLowerer()

    def lower_source(self, source):
        result = self.frontend.compile(source)

        if not result["success"]:
            self.fail(f"Frontend failed: {result['error']}")

        ir = self.generator.generate(result["ast"])
        return self.lowerer.lower(ir)

    def test_arithmetic_lowering(self):
        program = self.lower_source("x = 10 + 5")

        self.assertGreater(len(program.instructions), 0)

    def test_float_lowering(self):
        program = self.lower_source("x = 10.5 + 2.5")

        self.assertGreater(len(program.instructions), 0)

    def test_comparison_lowering(self):
        program = self.lower_source("x = 10 > 5")

        self.assertGreater(len(program.instructions), 0)

    def test_logical_lowering(self):
        program = self.lower_source("x = True and False")

        self.assertGreater(len(program.instructions), 0)

    def test_bitwise_lowering(self):
        program = self.lower_source("x = 6 & 3")

        self.assertGreater(len(program.instructions), 0)

    def test_shift_lowering(self):
        program = self.lower_source("x = 2 << 3")

        self.assertGreater(len(program.instructions), 0)

    def test_print_lowering(self):
        program = self.lower_source("print(10 + 20)")

        self.assertGreater(len(program.instructions), 0)

    def test_halt_instruction(self):
        program = self.lower_source("x = 10")

        self.assertEqual(
            program.instructions[-1].opcode,
            0x00
        )


if __name__ == "__main__":
    unittest.main()
