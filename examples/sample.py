
# examples/sample.py

# ==========================================
# PYTHON TO C++ MINI COMPILER
# COMPLETE ALU TEST PROGRAM
# ==========================================

# 1. INTEGER ARITHMETIC
a = 20
b = 6

print(a + b)
print(a - b)
print(a * b)
print(a / b)
print(a // b)
print(a % b)
print(a ** 2)


# 2. FLOAT ARITHMETIC
x = 10.5
y = 2.5

print(x + y)
print(x - y)
print(x * y)
print(x / y)
print(x // y)
print(x % y)
print(x ** 2)


# 3. MIXED INTEGER AND FLOAT
print(a + x)
print(a - y)
print(b * x)
print(a / y)
print(a // y)
print(a % y)
print(a ** 2.5)


# 4. INTEGER COMPARISON
print(a == b)
print(a != b)
print(a > b)
print(a < b)
print(a >= b)
print(a <= b)


# 5. FLOAT COMPARISON
print(x == y)
print(x != y)
print(x > y)
print(x < y)
print(x >= y)
print(x <= y)


# 6. MIXED COMPARISON
print(10 == 10.0)
print(10 != 10.5)
print(15 > 12.5)
print(5 < 8.5)


# 7. LOGICAL OPERATIONS
print(a > 5 and x < 20)
print(a < 5 or x > 10)
print(not (a == b))


# 8. BITWISE OPERATIONS
num1 = 12
num2 = 5

print(num1 & num2)
print(num1 | num2)
print(num1 ^ num2)
print(~num1)


# 9. SHIFT OPERATIONS
print(num1 << 2)
print(num1 >> 2)


# 10. UNARY OPERATIONS
print(+a)
print(-a)
print(+x)
print(-x)


# 11. BOOLEAN OPERATIONS
flag1 = True
flag2 = False

print(flag1)
print(flag2)
print(not flag1)
print(flag1 and flag2)
print(flag1 or flag2)


# 12. OPERATOR PRECEDENCE
print(10 + 5 * 2)
print((10 + 5) * 2)
print(2 ** 3 ** 2)
print(-2 ** 2)


# 13. NESTED EXPRESSIONS
result1 = (10 + 5) * (20 - 8)
result2 = (10.5 + 2.5) * (8.0 / 2.0)
result3 = (10 + 5.5) / (2 + 1)

print(result1)
print(result2)
print(result3)


# 14. FLOAT PRECISION
decimal1 = 0.1
decimal2 = 0.2

print(decimal1 + decimal2)
print(1.0 / 3.0)
print(10.123456789 * 2.0)


# 15. LARGE AND SMALL NUMBERS
large_number = 1000000
small_number = 0.000001

print(large_number * 2)
print(small_number * 10)
