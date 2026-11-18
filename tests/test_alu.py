
import unittest

from architecture.alu import ALU


class TestALU(unittest.TestCase):

    def setUp(self):
        self.alu = ALU()

    def test_addition(self):
        self.assertEqual(self.alu.execute("ADD", 10, 20), 30)

    def test_subtraction(self):
        self.assertEqual(self.alu.execute("SUB", 30, 10), 20)

    def test_multiplication(self):
        self.assertEqual(self.alu.execute("MUL", 5, 5), 25)

    def test_division(self):
        self.assertEqual(self.alu.execute("DIV", 20, 5), 4)

    def test_modulus(self):
        self.assertEqual(self.alu.execute("MOD", 20, 6), 2)

    def test_and(self):
        self.assertEqual(self.alu.execute("AND", 6, 3), 2)

    def test_or(self):
        self.assertEqual(self.alu.execute("OR", 6, 3), 7)

    def test_xor(self):
        self.assertEqual(self.alu.execute("XOR", 6, 3), 5)


if __name__ == "__main__":
    unittest.main()
