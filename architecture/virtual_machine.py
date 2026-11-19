
from architecture.instruction_set import Opcode
from architecture.alu import ALU, ALUError
from architecture.registers import RegisterFile
from architecture.memory import Memory


class VirtualMachineError(Exception):
    pass


class VirtualMachine:
    def __init__(self, trace=False, max_steps=1_000_000):
        self.alu = ALU()
        self.registers = RegisterFile()
        self.memory = Memory()

        self.trace = trace
        self.max_steps = max_steps
        self.halted = False
        self.output = []
        self.program = None

    # ---------------- PROGRAM LOADING ----------------

    def load_program(self, program):
        if not hasattr(program, "instructions"):
            raise VirtualMachineError(
                "Expected a BytecodeProgram with instructions."
            )

        self.program = program
        self.memory.reset()
        self.memory.load_instructions(program.instructions)

        self.registers.reset()
        self.halted = False
        self.output = []

    # ---------------- CONSTANTS AND VARIABLES ----------------

    def _constant(self, index):
        try:
            constant = self.program.get_constant(index)
        except Exception as exc:
            raise VirtualMachineError(
                f"Invalid constant index: {index}"
            ) from exc

        return getattr(constant, "value", constant)

    def _name(self, index):
        try:
            return self.program.get_name(index)
        except Exception as exc:
            raise VirtualMachineError(
                f"Invalid variable name index: {index}"
            ) from exc

    # ---------------- STACK OPERATIONS ----------------

    def _push(self, value):
        self.memory.push(value)
        self.registers.SP = self.memory.stack_size_used()

    def _pop(self):
        value = self.memory.pop()
        self.registers.SP = self.memory.stack_size_used()
        return value

    def _binary(self, operation):
        b = self._pop()
        a = self._pop()
        self._push(operation(a, b))

    def _unary(self, operation):
        value = self._pop()
        self._push(operation(value))

    # ---------------- OUTPUT ----------------

    def _print_value(self, value):
        if isinstance(value, bool):
            text = "True" if value else "False"
        else:
            text = str(value)

        self.output.append(text)
        print(text)

    # ---------------- INSTRUCTION EXECUTION ----------------

    def _execute_instruction(self, instruction):
        try:
            opcode = Opcode(instruction.opcode)
            operand = instruction.operand
        except (ValueError, TypeError, AttributeError) as exc:
            raise VirtualMachineError(
                f"Invalid instruction: {instruction}"
            ) from exc

        self.registers.IR = opcode.name
        self.registers.MAR = self.registers.PC
        self.registers.MDR = operand

        if self.trace:
            print(
                f"[PC={self.registers.PC:04}] "
                f"{opcode.name:<16} {operand}"
            )

        # -------- CONTROL --------

        if opcode == Opcode.HALT:
            self.halted = True
            return

        elif opcode == Opcode.POP:
            self._pop()

        # -------- LOAD AND STORE --------

        elif opcode in (
            Opcode.LOAD_INT,
            Opcode.LOAD_FLOAT,
            Opcode.LOAD_BOOL
        ):
            self._push(self._constant(operand))

        elif opcode == Opcode.LOAD_VAR:
            name = self._name(operand)
            self._push(self.memory.load_variable(name))

        elif opcode == Opcode.STORE_VAR:
            name = self._name(operand)
            value = self._pop()
            self.memory.store_variable(name, value)
            self.registers.ACC = value

        # -------- INTEGER ARITHMETIC --------

        elif opcode == Opcode.ADD_INT:
            self._binary(lambda a, b: self.alu.add(
                self._require_int(a), self._require_int(b)
            ))

        elif opcode == Opcode.SUB_INT:
            self._binary(lambda a, b: self.alu.subtract(
                self._require_int(a), self._require_int(b)
            ))

        elif opcode == Opcode.MUL_INT:
            self._binary(lambda a, b: self.alu.multiply(
                self._require_int(a), self._require_int(b)
            ))

        elif opcode == Opcode.DIV_INT:
            self._binary(self.alu.divide)

        elif opcode == Opcode.FLOOR_DIV_INT:
            self._binary(lambda a, b: self.alu.floor_divide(
                self._require_int(a), self._require_int(b)
            ))

        elif opcode == Opcode.MOD_INT:
            self._binary(lambda a, b: self.alu.modulo(
                self._require_int(a), self._require_int(b)
            ))

        elif opcode == Opcode.POWER_INT:
            self._binary(lambda a, b: self.alu.power(
                self._require_int(a), self._require_int(b)
            ))

        # -------- FLOAT ARITHMETIC --------

        elif opcode == Opcode.ADD_FLOAT:
            self._binary(self.alu.add)

        elif opcode == Opcode.SUB_FLOAT:
            self._binary(self.alu.subtract)

        elif opcode == Opcode.MUL_FLOAT:
            self._binary(self.alu.multiply)

        elif opcode == Opcode.DIV_FLOAT:
            self._binary(self.alu.divide)

        elif opcode == Opcode.FLOOR_DIV_FLOAT:
            self._binary(self.alu.floor_divide)

        elif opcode == Opcode.MOD_FLOAT:
            self._binary(self.alu.modulo)

        elif opcode == Opcode.POWER_FLOAT:
            self._binary(self.alu.power)

        # -------- COMPARISON --------

        elif opcode == Opcode.CMP_EQ:
            self._binary(self.alu.compare_equal)

        elif opcode == Opcode.CMP_NE:
            self._binary(self.alu.compare_not_equal)

        elif opcode == Opcode.CMP_LT:
            self._binary(self.alu.compare_less)

        elif opcode == Opcode.CMP_GT:
            self._binary(self.alu.compare_greater)

        elif opcode == Opcode.CMP_LE:
            self._binary(self.alu.compare_less_equal)

        elif opcode == Opcode.CMP_GE:
            self._binary(self.alu.compare_greater_equal)

        # -------- LOGICAL --------

        elif opcode == Opcode.TO_BOOL:
            self._unary(self.alu.to_bool)

        elif opcode == Opcode.LOGICAL_AND:
            self._binary(self.alu.logical_and)

        elif opcode == Opcode.LOGICAL_OR:
            self._binary(self.alu.logical_or)

        elif opcode == Opcode.LOGICAL_NOT:
            self._unary(self.alu.logical_not)

        # -------- BITWISE --------

        elif opcode == Opcode.BIT_AND:
            self._binary(self.alu.bitwise_and)

        elif opcode == Opcode.BIT_OR:
            self._binary(self.alu.bitwise_or)

        elif opcode == Opcode.BIT_XOR:
            self._binary(self.alu.bitwise_xor)

        elif opcode == Opcode.BIT_NOT:
            self._unary(self.alu.bitwise_not)

        elif opcode == Opcode.LSHIFT:
            self._binary(self.alu.left_shift)

        elif opcode == Opcode.RSHIFT:
            self._binary(self.alu.right_shift)

        # -------- UNARY --------

        elif opcode == Opcode.NEG:
            self._unary(self.alu.negate)

        elif opcode == Opcode.POS:
            self._unary(self.alu.positive)

        # -------- TYPE CONVERSION --------

        elif opcode == Opcode.INT_TO_FLOAT:
            self._unary(self.alu.int_to_float)

        elif opcode == Opcode.FLOAT_TO_INT:
            self._unary(self.alu.float_to_int)

        # -------- JUMPS --------

        elif opcode == Opcode.JUMP:
            self._jump(operand)

        elif opcode == Opcode.JUMP_IF_FALSE:
            condition = self._pop()

            if not bool(condition):
                self._jump(operand)

        elif opcode == Opcode.JUMP_IF_TRUE:
            condition = self._pop()

            if bool(condition):
                self._jump(operand)

        # -------- PRINT --------

        elif opcode == Opcode.PRINT_INT:
            value = self._pop()
            self._print_value(self._require_int(value))

        elif opcode == Opcode.PRINT_FLOAT:
            value = self._pop()

            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise VirtualMachineError(
                    "PRINT_FLOAT requires a numeric value."
                )

            self._print_value(value)

        elif opcode == Opcode.PRINT_BOOL:
            value = self._pop()

            if not isinstance(value, bool):
                raise VirtualMachineError(
                    "PRINT_BOOL requires a Boolean value."
                )

            self._print_value(value)

        else:
            raise VirtualMachineError(
                f"Unsupported opcode: {opcode.name}"
            )

        self.registers.set_flags(self.alu.get_flags())

        if self.memory.stack:
            self.registers.ACC = self.memory.peek()

    # ---------------- HELPERS ----------------

    @staticmethod
    def _require_int(value):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ALUError("Expected an integer operand.")
        return value

    def _jump(self, target):
        if not isinstance(target, int):
            raise VirtualMachineError("Jump target must be an integer.")

        if target < 0 or target >= len(self.memory.instructions):
            raise VirtualMachineError(
                f"Jump target out of range: {target}"
            )

        self.registers.PC = target

    # ---------------- MAIN EXECUTION LOOP ----------------

    def run(self, program=None):
        if program is not None:
            self.load_program(program)

        if self.program is None:
            raise VirtualMachineError("No program has been loaded.")

        steps = 0

        try:
            while not self.halted:
                if steps >= self.max_steps:
                    raise VirtualMachineError(
                        "Maximum instruction count exceeded."
                    )

                pc_before = self.registers.PC
                instruction = self.memory.fetch_instruction(pc_before)

                # Advance PC before executing. A jump replaces this value.
                self.registers.PC += 1

                self._execute_instruction(instruction)
                steps += 1

        except (ALUError, IndexError, TypeError, ValueError) as exc:
            raise VirtualMachineError(
                f"Execution failed at instruction "
                f"{self.registers.PC}: {exc}"
            ) from exc

        return {
            "success": True,
            "steps": steps,
            "output": self.output.copy(),
            "variables": self.memory.variables.copy(),
            "registers": {
                "PC": self.registers.PC,
                "SP": self.registers.SP,
                "ACC": self.registers.ACC,
                "FLAGS": self.registers.get_flags(),
            },
        }

    def reset(self):
        self.memory.reset()
        self.registers.reset()
        self.alu = ALU()
        self.halted = False
        self.output = []
        self.program = None

    def display_state(self):
        self.registers.display()
        self.memory.display_stack()
