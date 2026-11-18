
class Memory:

    def __init__(
        self,
        constants=None,
        variables=None,
        stack_size=1024
    ):

        self.constants = list(constants or [])

        self.variables = list(variables or [])

        self.stack = []

        self.stack_size = stack_size

        self.data_memory = {}

    # --------------------------------------
    # Constant Pool
    # --------------------------------------

    def load_constant(self, address):

        if not 0 <= address < len(self.constants):

            raise IndexError(
                "Invalid constant memory address"
            )

        return self.constants[address]

    # --------------------------------------
    # Variable Memory
    # --------------------------------------

    def load_variable(self, address):

        if not 0 <= address < len(self.variables):

            raise IndexError(
                "Invalid variable address"
            )

        return self.variables[address]

    def store_variable(self, address, value):

        if not 0 <= address < len(self.variables):

            raise IndexError(
                "Invalid variable address"
            )

        self.variables[address] = value

    # --------------------------------------
    # Stack Operations
    # --------------------------------------

    def push(self, value):

        if len(self.stack) >= self.stack_size:

            raise OverflowError(
                "Stack memory overflow"
            )

        self.stack.append(value)

    def pop(self):

        if not self.stack:

            raise RuntimeError(
                "Stack underflow"
            )

        return self.stack.pop()

    def peek(self):

        if not self.stack:

            raise RuntimeError(
                "Stack is empty"
            )

        return self.stack[-1]

    # --------------------------------------
    # Data Memory
    # --------------------------------------

    def write_memory(self, address, value):

        if address < 0:
            raise ValueError("Invalid memory address")

        self.data_memory[address] = value

    def read_memory(self, address):

        if address < 0:
            raise ValueError("Invalid memory address")

        return self.data_memory.get(address, 0)

    # --------------------------------------
    # Memory Status
    # --------------------------------------

    def display(self):

        print("\n========== MEMORY STATUS ==========")

        print("Constants:", self.constants)

        print("Variables:", self.variables)

        print("Stack:", self.stack)

        print("Data Memory:", self.data_memory)

        print("===================================")

    def reset_stack(self):

        self.stack.clear()
