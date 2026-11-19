
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from compiler.frontend import Frontend
from compiler.intermediate_code import (
    IntermediateCodeGenerator,
    IntermediateCodeLowerer
)
from compiler.cpp_generator import CppGenerator


class TestCppGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = CppGenerator()

    def compile_to_bytecode(self, source):
        frontend = Frontend()
        result = frontend.compile(source)

        if not result["success"]:
            self.fail(f"Frontend error: {result['error']}")

        ir_generator = IntermediateCodeGenerator()
        ir = ir_generator.generate(result["ast"])

        lowerer = IntermediateCodeLowerer()
        return lowerer.lower(ir)

    def generate_cpp(self, source):
        program = self.compile_to_bytecode(source)
        return self.generator.generate(program)

    def test_cpp_generation_returns_string(self):
        code = self.generate_cpp("x = 10")
        self.assertIsInstance(code, str)

    def test_cpp_headers(self):
        code = self.generate_cpp("x = 10")

        self.assertIn("#include", code)
        self.assertIn("int main", code)

    def test_integer_arithmetic_generation(self):
        code = self.generate_cpp("""
a = 10
b = 20
print(a + b)
""")

        self.assertIn("ADD_INT", code)

    def test_float_arithmetic_generation(self):
        code = self.generate_cpp("""
a = 2.5
b = 1.5
print(a + b)
""")

        self.assertIn("ADD_FLOAT", code)

    def test_comparison_generation(self):
        code = self.generate_cpp("""
a = 10
b = 5
print(a > b)
""")

        self.assertIn("CMP_GT", code)

    def test_bitwise_generation(self):
        code = self.generate_cpp("""
a = 6 & 3
print(a)
""")

        self.assertIn("BIT_AND", code)

    def test_logical_generation(self):
        code = self.generate_cpp("""
a = True and False
print(a)
""")

        self.assertIn("JUMP_IF_FALSE", code)

    def test_cpp_compilation_and_execution(self):
        compiler = shutil.which("g++")

        if compiler is None:
            self.skipTest("GCC g++ was not found in PATH.")

        code = self.generate_cpp("""
a = 10
b = 20
print(a + b)
""")

        with tempfile.TemporaryDirectory() as temp_dir:
            cpp_file = Path(temp_dir) / "generated.cpp"
            exe_file = Path(temp_dir) / "generated.exe"

            cpp_file.write_text(code, encoding="utf-8")

            build = subprocess.run(
                [
                    compiler,
                    "-std=c++17",
                    str(cpp_file),
                    "-o",
                    str(exe_file)
                ],
                capture_output=True,
                text=True
            )

            self.assertEqual(
                build.returncode,
                0,
                msg=build.stderr
            )

            execution = subprocess.run(
                [str(exe_file)],
                capture_output=True,
                text=True
            )

            self.assertEqual(
                execution.returncode,
                0,
                msg=execution.stderr
            )

            self.assertIn("30", execution.stdout)


if __name__ == "__main__":
    unittest.main()
