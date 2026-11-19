
class MemoryError(Exception):
    pass


class Memory:
    def __init__(
        self,
        data_size=65536,
        stack_size=65536,
        instruction_size=65536
    ):
        self.data_size = data_size
        self.stack_size = stack_size
        self.instruction_size = instruction_size

        self.data = [None] * data_size
        self.stack = []
        self.instructions = []

        self.variables = {}

    # ---------------- DATA MEMORY ----------------

    def read(self, address):
        self._check_address(address, self.data_size)
        return self.data[address]

    def write(self, address, value):
        self._check_address(address, self.data_size)
        self.data[address] = value

    # ---------------- STACK MEMORY ----------------

    def push(self, value):
        if len(self.stack) >= self.stack_size:
            raise MemoryError("Stack overflow.")

        self.stack.append(value)

    def pop(self):
        if not self.stack:
            raise MemoryError("Stack underflow.")

        return self.stack.pop()

    def peek(self):
        if not self.stack:
            raise MemoryError("Stack is empty.")

        return self.stack[-1]

    def stack_size_used(self):
        return len(self.stack)

    def clear_stack(self):
        self.stack.clear()

    # ---------------- INSTRUCTION MEMORY ----------------

    def load_instructions(self, instructions):
        if len(instructions) > self.instruction_size:
            raise MemoryError("Instruction memory capacity exceeded.")

        self.instructions = list(instructions)

    def fetch_instruction(self, address):
        if not isinstance(address, int):
            raise MemoryError("Instruction address must be an integer.")

        if address < 0 or address >= len(self.instructions):
            raise MemoryError(
                f"Invalid instruction address: {address}"
            )

        return self.instructions[address]

    # ---------------- VARIABLE STORAGE ----------------

    def store_variable(self, name, value):
        self.variables[name] = value

    def load_variable(self, name):
        if name not in self.variables:
            raise MemoryError(f"Undefined variable: {name}")

        return self.variables[name]

    # ---------------- UTILITIES ----------------

    @staticmethod
    def _check_address(address, size):
        if not isinstance(address, int):
            raise MemoryError("Memory address must be an integer.")

        if address < 0 or address >= size:
            raise MemoryError(
                f"Memory address out of range: {address}"
            )

    def reset(self):
        self.data = [None] * self.data_size
        self.stack.clear()
        self.instructions.clear()
        self.variables.clear()

    def display_stack(self):
        print("\n========== STACK ==========")

        if not self.stack:
            print("(empty)")
        else:
            for index, value in enumerate(reversed(self.stack)):
                print(f"STACK[{len(self.stack) - 1 - index}] = {value}")

        print("===========================\n")

    def display_memory(self, start=0, count=10):
        end = min(start + count, self.data_size)

        print("\n========== DATA MEMORY ==========")

        for address in range(start, end):
            print(f"MEM[{address}] = {self.data[address]}")

        print("=================================\n")
