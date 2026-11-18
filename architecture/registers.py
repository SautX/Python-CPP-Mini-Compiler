
class Registers:

    def __init__(self):

        # General-purpose registers
        self.general = {
            f"R{i}": 0 for i in range(8)
        }

        # Special-purpose registers
        self.PC = 0       # Program Counter
        self.SP = 0       # Stack Pointer
        self.ACC = 0      # Accumulator
        self.IR = 0       # Instruction Register

        # Processor flags
        self.FLAGS = {
            "ZERO": False,
            "NEGATIVE": False,
            "CARRY": False,
            "OVERFLOW": False
        }

    # --------------------------------------
    # General Register Operations
    # --------------------------------------

    def read(self, register):

        if register not in self.general:
            raise ValueError("Invalid register")

        return self.general[register]

    def write(self, register, value):

        if register not in self.general:
            raise ValueError("Invalid register")

        self.general[register] = value

    # --------------------------------------
    # Special Register Operations
    # --------------------------------------

    def update_pc(self, value):

        self.PC = value

    def increment_pc(self):

        self.PC += 1

    def update_sp(self, value):

        self.SP = value

    def update_acc(self, value):

        self.ACC = value

    def update_ir(self, value):

        self.IR = value

    # --------------------------------------
    # Flag Operations
    # --------------------------------------

    def update_flags(self, alu):

        self.FLAGS["ZERO"] = alu.zero_flag

        self.FLAGS["NEGATIVE"] = (
            alu.negative_flag
        )

        self.FLAGS["CARRY"] = (
            alu.carry_flag
        )

        self.FLAGS["OVERFLOW"] = (
            alu.overflow_flag
        )

    def get_flag(self, flag):

        return self.FLAGS.get(flag, False)

    # --------------------------------------
    # Display Register Status
    # --------------------------------------

    def display(self):

        print("\n========== REGISTER STATUS ==========")

        for name, value in self.general.items():

            print(f"{name}: {value}")

        print("-------------------------------------")

        print("PC :", self.PC)
        print("SP :", self.SP)
        print("ACC:", self.ACC)
        print("IR :", self.IR)

        print("-------------------------------------")

        for flag, value in self.FLAGS.items():

            print(f"{flag}: {value}")

        print("=====================================")

    def reset(self):

        for register in self.general:
            self.general[register] = 0

        self.PC = 0
        self.SP = 0
        self.ACC = 0
        self.IR = 0

        for flag in self.FLAGS:
            self.FLAGS[flag] = False
