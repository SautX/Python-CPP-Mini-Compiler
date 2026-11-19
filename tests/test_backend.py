
import unittest

from compiler.frontend import Frontend
from compiler.intermediate_code import (
    IntermediateCodeGenerator,
    IntermediateCodeLowerer
)
from compiler.optimizer import optimize_bytecode
from architecture.virtual_machine import VirtualMachine


class TestCompilerIntegration(unittest.TestCase):

    def compile_and_run(self, source):
        frontend = Frontend()
        result = frontend.compile(source)

        if not result["success"]:
            self.fail(f"Frontend error: {result['error']}")

        generator = IntermediateCodeGenerator()
        ir = generator.generate(result["ast"])

        lowerer = IntermediateCodeLowerer()
        program = lowerer.lower(ir)

        program = optimize_bytecode(program)

        vm = VirtualMachine(trace=False)
        execution = vm.run(program)

        return execution

    def test_integer_arithmetic(self):
        result = self.compile_and_run("""
a = 20
b = 5
print(a + b)
""")

        self.assertEqual(result["output"], ["25"])

    def test_float_arithmetic(self):
        result = self.compile_and_run("""
a = 2.5
b = 1.5
print(a + b)
""")

        self.assertAlmostEqual(float(result["output"][0]), 4.0)

    def test_comparison(self):
        result = self.compile_and_run("""
a = 10
b = 5
print(a > b)
""")

        self.assertEqual(result["output"], ["True"])

    def test_logical_operation(self):
        result = self.compile_and_run("""
a = True and False
print(a)
""")

        self.assertEqual(result["output"], ["False"])

    def test_bitwise_operation(self):
        result = self.compile_and_run("""
a = 6 & 3
print(a)
""")

        self.assertEqual(result["output"], ["2"])

    def test_shift_operation(self):
        result = self.compile_and_run("""
a = 2 << 3
print(a)
""")

        self.assertEqual(result["output"], ["16"])

    def test_type_conversion(self):
        result = self.compile_and_run("""
a = 5
b = 2.5
c = a + b
print(c)
""")

        self.assertAlmostEqual(float(result["output"][0]), 7.5)

    def test_multiple_operations(self):
        result = self.compile_and_run("""
a = 20
b = 5
c = (a + b) * 2
print(c)
""")

        self.assertEqual(result["output"], ["50"])


if __name__ == "__main__":
    unittest.main()
