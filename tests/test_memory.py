
import unittest

from architecture.memory import Memory, MemoryError


class TestMemory(unittest.TestCase):

    def setUp(self):
        self.memory = Memory(
            data_size=100,
            stack_size=10,
            instruction_size=100
        )

    # Data memory
    def test_write_and_read(self):
        self.memory.write(5, 100)
        self.assertEqual(self.memory.read(5), 100)

    def test_empty_memory(self):
        self.assertIsNone(self.memory.read(0))

    def test_invalid_address(self):
        with self.assertRaises(MemoryError):
            self.memory.read(100)

    def test_negative_address(self):
        with self.assertRaises(MemoryError):
            self.memory.write(-1, 10)

    # Stack memory
    def test_stack_push(self):
        self.memory.push(10)
        self.assertEqual(self.memory.peek(), 10)

    def test_stack_pop(self):
        self.memory.push(10)
        self.memory.push(20)

        self.assertEqual(self.memory.pop(), 20)
        self.assertEqual(self.memory.pop(), 10)

    def test_stack_underflow(self):
        with self.assertRaises(MemoryError):
            self.memory.pop()

    def test_stack_overflow(self):
        for value in range(10):
            self.memory.push(value)

        with self.assertRaises(MemoryError):
            self.memory.push(11)

    def test_stack_size(self):
        self.memory.push(10)
        self.memory.push(20)

        self.assertEqual(self.memory.stack_size_used(), 2)

    # Variable storage
    def test_store_variable(self):
        self.memory.store_variable("total", 500)

        self.assertEqual(
            self.memory.load_variable("total"),
            500
        )

    def test_undefined_variable(self):
        with self.assertRaises(MemoryError):
            self.memory.load_variable("unknown")

    # Instruction memory
    def test_load_instructions(self):
        instructions = [1, 2, 3]

        self.memory.load_instructions(instructions)

        self.assertEqual(
            self.memory.fetch_instruction(0),
            1
        )

    def test_invalid_instruction_address(self):
        self.memory.load_instructions([1, 2])

        with self.assertRaises(MemoryError):
            self.memory.fetch_instruction(5)

    # Reset
    def test_reset(self):
        self.memory.write(0, 100)
        self.memory.push(50)
        self.memory.store_variable("x", 10)

        self.memory.reset()

        self.assertIsNone(self.memory.read(0))
        self.assertEqual(self.memory.stack, [])
        self.assertEqual(self.memory.variables, {})


if __name__ == "__main__":
    unittest.main()
