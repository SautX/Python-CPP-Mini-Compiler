
# examples/test_bytecode_pipeline.py

from compiler.frontend import Frontend
from compiler.intermediate_code import (
    IntermediateCodeGenerator,
    IntermediateCodeLowerer
)
from compiler.bytecode_decoder import BytecodeDecoder


SOURCE = """
a = 20
b = 6
x = 10.5
y = 2.5

print(a + b)
print(x + y)
print(a + x)
print(a / b)
print(a // b)
print(a % b)
print(a ** 2)

print(a > b)
print(x < y)
print(a == 20)

print(a > 10 and x > 5)
print(a < 5 or x > 10)
print(not (a == b))

print(a & b)
print(a | b)
print(a ^ b)
print(a << 2)
print(a >> 1)
print(~a)

print(-x)
print(+a)
"""


def main():

    print("\n========== FRONTEND ==========")

    frontend = Frontend()
    result = frontend.compile(SOURCE)

    if not result["success"]:
        print("Frontend error:", result["error"])
        return

    print("Frontend compilation successful")

    print("\n========== INTERMEDIATE CODE ==========")

    generator = IntermediateCodeGenerator()
    ir = generator.compile(result["ast"])

    for index, instruction in enumerate(ir):
        print(f"{index:04d}: {instruction}")

    print("\n========== BYTECODE GENERATION ==========")

    lowerer = IntermediateCodeLowerer()
    program = lowerer.lower(ir)

    program.dump()

    print("\n========== BYTECODE EXECUTION ==========")

    decoder = BytecodeDecoder(program)
    execution_result = decoder.execute()

    print("\n========== FINAL VARIABLES ==========")

    for name, value in execution_result["variables"].items():
        print(f"{name} = {value!r} ({type(value).__name__})")


if __name__ == "__main__":
    main()
