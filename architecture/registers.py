
class RegisterError(Exception):
    pass


class RegisterFile:
    """
    Educational CPU register model.

    PC  : Program Counter
    SP  : Stack Pointer
    ACC : Accumulator
    IR  : Instruction Register
    MAR : Memory Address Register
    MDR : Memory Data Register
    FLAGS: ALU status flags
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.PC = 0
        self.SP = 0
        self.ACC = 0
        self.IR = None
        self.MAR = 0
        self.MDR = None

        self.FLAGS = {
            "zero": False,
            "negative": False,
            "carry": False,
            "overflow": False,
        }

    def read(self, name):
        name = name.upper()

        if not hasattr(self, name):
            raise RegisterError(f"Unknown register: {name}")

        return getattr(self, name)

    def write(self, name, value):
        name = name.upper()

        if not hasattr(self, name):
            raise RegisterError(f"Unknown register: {name}")

        if name == "PC" and (
            not isinstance(value, int) or value < 0
        ):
            raise RegisterError("PC must be a non-negative integer.")

        if name == "SP" and (
            not isinstance(value, int) or value < 0
        ):
            raise RegisterError("SP must be a non-negative integer.")

        setattr(self, name, value)

    def increment_pc(self):
        self.PC += 1

    def set_accumulator(self, value):
        self.ACC = value

    def set_flags(self, flags):
        self.FLAGS.update(flags)

    def get_flags(self):
        return self.FLAGS.copy()

    def display(self):
        print("\n========== CPU REGISTERS ==========")
        print(f"PC    : {self.PC}")
        print(f"SP    : {self.SP}")
        print(f"ACC   : {self.ACC}")
        print(f"IR    : {self.IR}")
        print(f"MAR   : {self.MAR}")
        print(f"MDR   : {self.MDR}")
        print(f"FLAGS : {self.FLAGS}")
        print("===================================\n")
