
import unittest

from compiler.frontend import Frontend
from compiler.intermediate_code import (
    IntermediateCodeGenerator,
    IntermediateCodeLowerer
)
from compiler.optimizer import optimize_bytecode
from architecture.virtual_machine import VirtualMachine


class TestOptimizer(unittest.TestCase):

    def compile_to_bytecode(self, source):
        frontend = Frontend()
        result = frontend.compile(source)

        if not result["success"]:
            self.fail(f"Frontend error: {result['error']}")

        generator = IntermediateCodeGenerator()
        ir = generator.generate(result["ast"])

        lowerer = IntermediateCodeLowerer()
        return lowerer.lower(ir)

    def execute(self, program):
        vm = VirtualMachine(trace=False)
        return vm.run(program)["output"]

    def test_integer_constant_folding(self):
        source = """
x = 10 + 20
print(x)
"""
        program = self.compile_to_bytecode(source)
        optimized = optimize_bytecode(program)

        self.assertEqual(self.execute(program), self.execute(optimized))
        self.assertEqual(self.execute(optimized), ["30"])

    def test_float_constant_folding(self):
        source = """
x = 2.5 + 1.5
print(x)
"""
        program = self.compile_to_bytecode(source)
        optimized = optimize_bytecode(program)

        self.assertEqual(self.execute(program), self.execute(optimized))
        self.assertAlmostEqual(float(self.execute(optimized)[0]), 4.0)

    def test_comparison_optimization(self):
        source = """
x = 10 > 5
print(x)
"""
        program = self.compile_to_bytecode(source)
        optimized = optimize_bytecode(program)

        self.assertEqual(self.execute(program), self.execute(optimized))
        self.assertEqual(self.execute(optimized), ["True"])

    def test_multiplication_optimization(self):
        source = """
x = 5 * 4
print(x)
"""
        program = self.compile_to_bytecode(source)
        optimized = optimize_bytecode(program)

        self.assertEqual(self.execute(program), self.execute(optimized))
        self.assertEqual(self.execute(optimized), ["20"])

    def test_division_by_zero_is_not_folded(self):
        source = """
x = 10 / 0
print(x)
"""
        program = self.compile_to_bytecode(source)
        optimized = optimize_bytecode(program)

        self.assertEqual(len(optimized.instructions), len(program.instructions))

    def test_variable_expression(self):
        source = """
a = 10
b = 20
c = a + b
print(c)
"""
        program = self.compile_to_bytecode(source)
        optimized = optimize_bytecode(program)

        self.assertEqual(self.execute(program), self.execute(optimized))
        self.assertEqual(self.execute(optimized), ["30"])


if __name__ == "__main__":
    unittest.main()
