
import unittest

from architecture.alu import ALU, ALUError


class TestALU(unittest.TestCase):

    def setUp(self):
        self.alu = ALU()

    # Arithmetic
    def test_addition(self):
        self.assertEqual(self.alu.add(10, 5), 15)

    def test_subtraction(self):
        self.assertEqual(self.alu.subtract(10, 5), 5)

    def test_multiplication(self):
        self.assertEqual(self.alu.multiply(10, 5), 50)

    def test_division(self):
        self.assertEqual(self.alu.divide(10, 4), 2.5)

    def test_floor_division(self):
        self.assertEqual(self.alu.floor_divide(10, 3), 3)

    def test_modulo(self):
        self.assertEqual(self.alu.modulo(10, 3), 1)

    def test_power(self):
        self.assertEqual(self.alu.power(2, 4), 16)

    def test_division_by_zero(self):
        with self.assertRaises(ALUError):
            self.alu.divide(10, 0)

    # Float arithmetic
    def test_float_addition(self):
        self.assertAlmostEqual(self.alu.add(2.5, 1.5), 4.0)

    def test_float_multiplication(self):
        self.assertAlmostEqual(self.alu.multiply(2.5, 2.0), 5.0)

    # Comparison
    def test_comparisons(self):
        self.assertTrue(self.alu.compare_equal(5, 5))
        self.assertTrue(self.alu.compare_not_equal(5, 3))
        self.assertTrue(self.alu.compare_less(3, 5))
        self.assertTrue(self.alu.compare_greater(5, 3))
        self.assertTrue(self.alu.compare_less_equal(5, 5))
        self.assertTrue(self.alu.compare_greater_equal(5, 5))

    # Logical
    def test_logical_operations(self):
        self.assertTrue(self.alu.logical_and(True, True))
        self.assertFalse(self.alu.logical_and(True, False))
        self.assertTrue(self.alu.logical_or(False, True))
        self.assertFalse(self.alu.logical_or(False, False))
        self.assertFalse(self.alu.logical_not(True))
        self.assertTrue(self.alu.to_bool(10))

    # Bitwise
    def test_bitwise_operations(self):
        self.assertEqual(self.alu.bitwise_and(6, 3), 2)
        self.assertEqual(self.alu.bitwise_or(6, 3), 7)
        self.assertEqual(self.alu.bitwise_xor(6, 3), 5)
        self.assertEqual(self.alu.bitwise_not(5), ~5)
        self.assertEqual(self.alu.left_shift(2, 3), 16)
        self.assertEqual(self.alu.right_shift(16, 2), 4)

    def test_negative_shift(self):
        with self.assertRaises(ALUError):
            self.alu.left_shift(2, -1)

    # Unary
    def test_unary_operations(self):
        self.assertEqual(self.alu.negate(10), -10)
        self.assertEqual(self.alu.positive(-10), -10)

    # Type conversion
    def test_type_conversion(self):
        self.assertEqual(self.alu.int_to_float(5), 5.0)
        self.assertEqual(self.alu.float_to_int(5.8), 5)
        self.assertEqual(self.alu.to_bool(1), True)
        self.assertEqual(self.alu.to_bool(0), False)

    # Flags
    def test_zero_flag(self):
        self.alu.subtract(5, 5)
        self.assertTrue(self.alu.get_flags()["zero"])

    def test_negative_flag(self):
        self.alu.subtract(3, 8)
        self.assertTrue(self.alu.get_flags()["negative"])


if __name__ == "__main__":
    unittest.main()
