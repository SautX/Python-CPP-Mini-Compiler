
class ALU:

    def __init__(self):

        self.result = 0

        self.zero_flag = False
        self.negative_flag = False
        self.carry_flag = False
        self.overflow_flag = False

    # --------------------------------------
    # Update Processor Flags
    # --------------------------------------

    def update_flags(self, result):

        self.result = result

        self.zero_flag = (result == 0)
        self.negative_flag = (result < 0)

        return result

    # --------------------------------------
    # Arithmetic Operations
    # --------------------------------------

    def add(self, a, b):

        return self.update_flags(a + b)

    def subtract(self, a, b):

        return self.update_flags(a - b)

    def multiply(self, a, b):

        return self.update_flags(a * b)

    def divide(self, a, b):

        if b == 0:
            raise ZeroDivisionError(
                "ALU division by zero"
            )

        return self.update_flags(a // b)

    def modulo(self, a, b):

        if b == 0:
            raise ZeroDivisionError(
                "ALU modulo by zero"
            )

        return self.update_flags(a % b)

    def negate(self, a):

        return self.update_flags(-a)

    # --------------------------------------
    # Logical Operations
    # --------------------------------------

    def bitwise_and(self, a, b):

        return self.update_flags(a & b)

    def bitwise_or(self, a, b):

        return self.update_flags(a | b)

    def bitwise_xor(self, a, b):

        return self.update_flags(a ^ b)

    def bitwise_not(self, a):

        return self.update_flags(~a)

    # --------------------------------------
    # Shift Operations
    # --------------------------------------

    def shift_left(self, a, b):

        return self.update_flags(a << b)

    def shift_right(self, a, b):

        return self.update_flags(a >> b)

    # --------------------------------------
    # Comparison
    # --------------------------------------

    def compare(self, a, b):

        result = a - b

        self.update_flags(result)

        return result
