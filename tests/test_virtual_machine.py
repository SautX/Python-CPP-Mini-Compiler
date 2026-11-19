
import unittest

from compiler.frontend import Frontend
from compiler.intermediate_code import (
    IntermediateCodeGenerator,
    IntermediateCodeLowerer
)
from architecture.virtual_machine import (
    VirtualMachine,
    VirtualMachineError
)


class TestVirtualMachine(unittest.TestCase):

    def setUp(self):
        self.vm = VirtualMachine(trace=False)

    def compile_program(self, source):
        frontend = Frontend()
        result = frontend.compile(source)

        if not result["success"]:
            self.fail(f"Frontend error: {result['error']}")

        generator = IntermediateCodeGenerator()
        ir = generator.generate(result["ast"])

        lowerer = IntermediateCodeLowerer()
        return lowerer.lower(ir)

    def run_source(self, source):
        program = self.compile_program(source)
        return self.vm.run(program)

    # Arithmetic execution
    def test_integer_addition(self):
        result = self.run_source("""
a = 10
b = 20
print(a + b)
""")
        self.assertEqual(result["output"], ["30"])

    def test_float_addition(self):
        result = self.run_source("""
a = 2.5
b = 1.5
print(a + b)
""")
        self.assertAlmostEqual(float(result["output"][0]), 4.0)

    # Variable storage
    def test_variable_storage(self):
        result = self.run_source("""
x = 100
print(x)
""")
        self.assertEqual(result["variables"]["x"], 100)
        self.assertEqual(result["output"], ["100"])

    # Stack
    def test_stack_is_empty_after_print(self):
        self.run_source("""
x = 10
print(x)
""")
        self.assertEqual(self.vm.memory.stack_size_used(), 0)

    # Comparison
    def test_comparison_execution(self):
        result = self.run_source("""
a = 10
b = 5
print(a > b)
""")
        self.assertEqual(result["output"], ["True"])

    # Logical
    def test_logical_execution(self):
        result = self.run_source("""
x = True and False
print(x)
""")
        self.assertEqual(result["output"], ["False"])

    # Bitwise
    def test_bitwise_execution(self):
        result = self.run_source("""
x = 6 & 3
print(x)
""")
        self.assertEqual(result["output"], ["2"])

    def test_shift_execution(self):
        result = self.run_source("""
x = 2 << 3
print(x)
""")
        self.assertEqual(result["output"], ["16"])

    # Multiple statements
    def test_multiple_instructions(self):
        result = self.run_source("""
a = 10
b = 20
c = a + b
print(c)
""")
        self.assertEqual(result["output"], ["30"])

    # Program completion
    def test_program_halts(self):
        self.run_source("x = 10")
        self.assertTrue(self.vm.halted)

    # Invalid program
    def test_run_without_program(self):
        with self.assertRaises(VirtualMachineError):
            VirtualMachine().run()


if __name__ == "__main__":
    unittest.main()
