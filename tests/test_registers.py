
import unittest

from architecture.registers import RegisterFile, RegisterError


class TestRegisters(unittest.TestCase):

    def setUp(self):
        self.registers = RegisterFile()

    def test_initial_values(self):
        self.assertEqual(self.registers.PC, 0)
        self.assertEqual(self.registers.SP, 0)
        self.assertEqual(self.registers.ACC, 0)

    def test_program_counter(self):
        self.registers.write("PC", 10)
        self.assertEqual(self.registers.read("PC"), 10)

    def test_stack_pointer(self):
        self.registers.write("SP", 5)
        self.assertEqual(self.registers.read("SP"), 5)

    def test_accumulator(self):
        self.registers.set_accumulator(100)
        self.assertEqual(self.registers.ACC, 100)

    def test_increment_pc(self):
        self.registers.increment_pc()
        self.assertEqual(self.registers.PC, 1)

    def test_instruction_register(self):
        self.registers.write("IR", "ADD_INT")
        self.assertEqual(self.registers.IR, "ADD_INT")

    def test_memory_address_register(self):
        self.registers.write("MAR", 20)
        self.assertEqual(self.registers.MAR, 20)

    def test_memory_data_register(self):
        self.registers.write("MDR", 500)
        self.assertEqual(self.registers.MDR, 500)

    def test_set_flags(self):
        flags = {
            "zero": True,
            "negative": False,
            "carry": False,
            "overflow": False
        }

        self.registers.set_flags(flags)

        self.assertTrue(self.registers.get_flags()["zero"])

    def test_invalid_register(self):
        with self.assertRaises(RegisterError):
            self.registers.read("UNKNOWN")

    def test_negative_program_counter(self):
        with self.assertRaises(RegisterError):
            self.registers.write("PC", -1)

    def test_negative_stack_pointer(self):
        with self.assertRaises(RegisterError):
            self.registers.write("SP", -1)

    def test_reset(self):
        self.registers.write("PC", 10)
        self.registers.write("ACC", 50)

        self.registers.reset()

        self.assertEqual(self.registers.PC, 0)
        self.assertEqual(self.registers.ACC, 0)


if __name__ == "__main__":
    unittest.main()
