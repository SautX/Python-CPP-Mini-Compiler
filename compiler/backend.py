from .bytecode import OPCODES


def generate_cpp(program):

    instructions = []

    for instruction in program.instructions:

        instructions.append(
            f"    {{{OPCODES[instruction.opcode]}, "
            f"{instruction.operand}}},"
        )

    constants = (
        ", ".join(
            str(value)
            for value in program.constants
        ) or "0"
    )

    variable_count = max(
        1,
        len(program.variables)
    )

    cpp_code = r'''
#include <iostream>
#include <vector>
#include <stdexcept>
#include <cstdint>

using namespace std;

struct Instruction {
    uint8_t opcode;
    uint16_t operand;
};

int main() {

    const long long constants[] = {
''' + constants + r'''
    };

    const Instruction program[] = {
''' + "\n".join(instructions) + r'''
    };

    vector<long long> stack;

    vector<long long> variables(''' + str(variable_count) + r''', 0);

    auto pop = [&]() -> long long {

        if (stack.empty())
            throw runtime_error("Stack underflow");

        long long value = stack.back();

        stack.pop_back();

        return value;
    };

    const size_t count =
        sizeof(program) / sizeof(program[0]);

    try {

        for (size_t pc = 0; pc < count; pc++) {

            Instruction ins = program[pc];

            switch (ins.opcode) {

                case 0x01:
                    if (ins.operand >=
                        sizeof(constants) / sizeof(constants[0]))
                        throw runtime_error("Invalid constant index");

                    stack.push_back(constants[ins.operand]);
                    break;

                case 0x02:
                    variables.at(ins.operand) = pop();
                    break;

                case 0x03:
                    stack.push_back(variables.at(ins.operand));
                    break;

                case 0x04: {
                    long long b = pop();
                    long long a = pop();
                    stack.push_back(a + b);
                    break;
                }

                case 0x05: {
                    long long b = pop();
                    long long a = pop();
                    stack.push_back(a - b);
                    break;
                }

                case 0x06: {
                    long long b = pop();
                    long long a = pop();
                    stack.push_back(a * b);
                    break;
                }

                case 0x07: {
                    long long b = pop();
                    long long a = pop();

                    if (b == 0)
                        throw runtime_error("Division by zero");

                    stack.push_back(a / b);
                    break;
                }

                case 0x08: {
                    long long b = pop();
                    long long a = pop();

                    if (b == 0)
                        throw runtime_error("Modulo by zero");

                    stack.push_back(a % b);
                    break;
                }

                case 0x09:
                    cout << pop() << endl;
                    break;

                case 0x0A:
                    return 0;

                case 0x0B:
                    stack.push_back(-pop());
                    break;

                default:
                    throw runtime_error("Unknown opcode");
            }
        }

    }
    catch (const exception& error) {

        cerr << "Runtime error: "
             << error.what() << endl;

        return 1;
    }

    return 0;
}
'''

    return cpp_code