
from .instruction_set import OPCODES
from .alu import ALU
from .registers import Registers
from .memory import Memory


class VirtualMachine:

    def __init__(self, program, debug=False):

        self.program = program

        self.alu = ALU()

        self.registers = Registers()

        self.memory = Memory(
            constants=program.constants,
            variables=[0] * len(program.variables)
        )

        self.debug = debug

        self.running = False

        self.instruction_count = 0

    # --------------------------------------
    # Stack Helpers
    # --------------------------------------

    def push(self, value):

        self.memory.push(value)

        self.registers.update_sp(
            len(self.memory.stack)
        )

    def pop(self):

        value = self.memory.pop()

        self.registers.update_sp(
            len(self.memory.stack)
        )

        return value

    # --------------------------------------
    # ALU Execution
    # --------------------------------------

    def execute_alu(self, opcode):

        b = self.pop()
        a = self.pop()

        operations = {

            "ADD": self.alu.add,
            "SUB": self.alu.subtract,
            "MUL": self.alu.multiply,
            "DIV": self.alu.divide,
            "MOD": self.alu.modulo,

            "AND": self.alu.bitwise_and,
            "OR": self.alu.bitwise_or,
            "XOR": self.alu.bitwise_xor,

            "SHL": self.alu.shift_left,
            "SHR": self.alu.shift_right
        }

        if opcode not in operations:

            raise ValueError(
                f"Unsupported ALU operation: {opcode}"
            )

        result = operations[opcode](a, b)

        self.push(result)

        self.registers.update_acc(result)

        self.registers.update_flags(self.alu)

    # --------------------------------------
    # Instruction Execution
    # --------------------------------------

    def execute(self, instruction):

        opcode = instruction.opcode

        operand = instruction.operand

        if opcode == "NOP":

            pass

        elif opcode == "LOAD_CONST":

            value = self.memory.load_constant(operand)

            self.push(value)

            self.registers.update_acc(value)

        elif opcode == "STORE_VAR":

            value = self.pop()

            self.memory.store_variable(
                operand,
                value
            )

        elif opcode == "LOAD_VAR":

            value = self.memory.load_variable(
                operand
            )

            self.push(value)

            self.registers.update_acc(value)

        elif opcode in (
            "ADD", "SUB", "MUL", "DIV", "MOD",
            "AND", "OR", "XOR", "SHL", "SHR"
        ):

            self.execute_alu(opcode)

        elif opcode == "NEG":

            value = self.pop()

            result = self.alu.negate(value)

            self.push(result)

            self.registers.update_acc(result)

            self.registers.update_flags(self.alu)

        elif opcode == "NOT":

            value = self.pop()

            result = self.alu.bitwise_not(value)

            self.push(result)

            self.registers.update_acc(result)

            self.registers.update_flags(self.alu)

        elif opcode == "PRINT":

            print(self.pop())

        elif opcode == "CMP":

            b = self.pop()
            a = self.pop()

            self.alu.compare(a, b)

            self.registers.update_acc(
                self.alu.result
            )

            self.registers.update_flags(
                self.alu
            )

        elif opcode == "JMP":

            self.registers.update_pc(operand)

        elif opcode == "JZ":

            if self.registers.get_flag("ZERO"):

                self.registers.update_pc(operand)

        elif opcode == "JNZ":

            if not self.registers.get_flag("ZERO"):

                self.registers.update_pc(operand)

        elif opcode == "HALT":

            self.running = False

        else:

            raise ValueError(
                f"Unknown instruction: {opcode}"
            )

    # --------------------------------------
    # Fetch-Decode-Execute Cycle
    # --------------------------------------

    def step(self):

        pc = self.registers.PC

        if not 0 <= pc < len(self.program.instructions):

            self.running = False
            return False

        instruction = self.program.instructions[pc]

        # FETCH
        self.registers.update_ir(
            instruction.encode()
        )

        # Move to next instruction
        self.registers.increment_pc()

        # DECODE and EXECUTE
        self.execute(instruction)

        self.instruction_count += 1

        if self.debug:

            print(
                f"\nExecuted PC={pc}: "
                f"{instruction.opcode}"
            )

            self.registers.display()

            self.memory.display()

        return True

    # --------------------------------------
    # Run Virtual Machine
    # --------------------------------------

    def run(self):

        self.running = True

        print("\n========== VIRTUAL MACHINE ==========")

        try:

            while self.running:

                self.step()

        finally:

            self.running = False

        print("\nExecution completed.")

        print(
            "Total instructions executed:",
            self.instruction_count
        )

        if self.debug:

            self.registers.display()
            self.memory.display()

        return self.memory.variables

    # --------------------------------------
    # Reset Processor
    # --------------------------------------

    def reset(self):

        self.registers.reset()

        self.memory.reset_stack()

        self.instruction_count = 0

        self.running = False

