
import unittest

from compiler.frontend import compile_source_to_bytecode
from compiler.backend import generate_cpp


class TestBackend(unittest.TestCase):

    def test_cpp_generation(self):

        source = """
a = 10
b = 20
c = a + b
print(c)
"""

        program = compile_source_to_bytecode(source)
        cpp_code = generate_cpp(program)

        self.assertIsInstance(cpp_code, str)
        self.assertIn("#include", cpp_code)
        self.assertIn("int main", cpp_code)

    def test_cpp_print_generation(self):

        source = """
a = 10
print(a)
"""

        program = compile_source_to_bytecode(source)
        cpp_code = generate_cpp(program)

        self.assertIn("cout", cpp_code)


if __name__ == "__main__":
    unittest.main()
