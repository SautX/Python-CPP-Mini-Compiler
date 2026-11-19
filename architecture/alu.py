
import math


class ALUError(Exception):
    """Raised when an invalid ALU operation occurs."""


class ALU:
    def __init__(self):
        self.zero_flag = False
        self.negative_flag = False
        self.carry_flag = False
        self.overflow_flag = False

    def _update_flags(self, result):
        self.zero_flag = result == 0
        self.negative_flag = (
            isinstance(result, (int, float)) and result < 0
        )
        return result

    def _integer(self, value):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ALUError("Integer operation requires integer operands.")
        return value

    def _number(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ALUError("Numeric operation requires int or float operands.")
        return value

    # ---------------- ARITHMETIC ----------------

    def add(self, a, b):
        return self._update_flags(self._number(a) + self._number(b))

    def subtract(self, a, b):
        return self._update_flags(self._number(a) - self._number(b))

    def multiply(self, a, b):
        return self._update_flags(self._number(a) * self._number(b))

    def divide(self, a, b):
        self._number(a)
        self._number(b)

        if b == 0:
            raise ALUError("Division by zero.")

        return self._update_flags(a / b)

    def floor_divide(self, a, b):
        self._number(a)
        self._number(b)

        if b == 0:
            raise ALUError("Floor division by zero.")

        return self._update_flags(a // b)

    def modulo(self, a, b):
        self._number(a)
        self._number(b)

        if b == 0:
            raise ALUError("Modulo by zero.")

        return self._update_flags(a % b)

    def power(self, a, b):
        self._number(a)
        self._number(b)

        try:
            result = a ** b
        except (OverflowError, ValueError, ZeroDivisionError) as exc:
            raise ALUError(str(exc)) from exc

        if isinstance(result, complex):
            raise ALUError("Complex results are not supported.")

        return self._update_flags(result)

    # ---------------- COMPARISON ----------------

    def compare_equal(self, a, b):
        return self._update_flags(a == b)

    def compare_not_equal(self, a, b):
        return self._update_flags(a != b)

    def compare_less(self, a, b):
        return self._update_flags(a < b)

    def compare_greater(self, a, b):
        return self._update_flags(a > b)

    def compare_less_equal(self, a, b):
        return self._update_flags(a <= b)

    def compare_greater_equal(self, a, b):
        return self._update_flags(a >= b)

    # ---------------- LOGICAL ----------------

    def logical_and(self, a, b):
        return self._update_flags(bool(a) and bool(b))

    def logical_or(self, a, b):
        return self._update_flags(bool(a) or bool(b))

    def logical_not(self, value):
        return self._update_flags(not bool(value))

    def to_bool(self, value):
        return self._update_flags(bool(value))

    # ---------------- BITWISE ----------------

    def bitwise_and(self, a, b):
        return self._update_flags(
            self._integer(a) & self._integer(b)
        )

    def bitwise_or(self, a, b):
        return self._update_flags(
            self._integer(a) | self._integer(b)
        )

    def bitwise_xor(self, a, b):
        return self._update_flags(
            self._integer(a) ^ self._integer(b)
        )

    def bitwise_not(self, value):
        return self._update_flags(~self._integer(value))

    def left_shift(self, a, b):
        a = self._integer(a)
        b = self._integer(b)

        if b < 0:
            raise ALUError("Negative shift count.")

        return self._update_flags(a << b)

    def right_shift(self, a, b):
        a = self._integer(a)
        b = self._integer(b)

        if b < 0:
            raise ALUError("Negative shift count.")

        return self._update_flags(a >> b)

    # ---------------- UNARY ----------------

    def negate(self, value):
        return self._update_flags(-self._number(value))

    def positive(self, value):
        return self._update_flags(+self._number(value))

    # ---------------- TYPE CONVERSION ----------------

    def int_to_float(self, value):
        return self._update_flags(float(self._integer(value)))

    def float_to_int(self, value):
        value = self._number(value)

        if isinstance(value, float) and not math.isfinite(value):
            raise ALUError("Cannot convert a non-finite float to int.")

        return self._update_flags(int(value))

    def get_flags(self):
        return {
            "zero": self.zero_flag,
            "negative": self.negative_flag,
            "carry": self.carry_flag,
            "overflow": self.overflow_flag,
        }
