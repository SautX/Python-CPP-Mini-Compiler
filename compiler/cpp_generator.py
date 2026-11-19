
# compiler/cpp_generator.py

from .bytecode import Opcode, BytecodeProgram


class CppGeneratorError(Exception):
    pass


class CppGenerator:

    def __init__(self, program):
        if not isinstance(program, BytecodeProgram):
            raise TypeError("Expected BytecodeProgram")

        self.program = program

    def generate(self):

        instructions = self.program.instructions
        constants = self.program.constants
        names = self.program.names

        lines = [
            "#include <iostream>",
            "#include <vector>",
            "#include <variant>",
            "#include <string>",
            "#include <unordered_map>",
            "#include <cmath>",
            "#include <cstdint>",
            "#include <stdexcept>",
            "#include <iomanip>",
            "#include <limits>",
            "",
            "using namespace std;",
            "",
            "using Value = variant<int64_t, double, bool>;",
            "",
            "double number(const Value& v) {",
            "    if (holds_alternative<int64_t>(v))",
            "        return static_cast<double>(get<int64_t>(v));",
            "    if (holds_alternative<double>(v))",
            "        return get<double>(v);",
            "    if (holds_alternative<bool>(v))",
            "        return get<bool>(v) ? 1.0 : 0.0;",
            '    throw runtime_error("Invalid numeric value");',
            "}",
            "",
            "int64_t integer(const Value& v) {",
            "    if (!holds_alternative<int64_t>(v))",
            '        throw runtime_error("Integer operand required");',
            "    return get<int64_t>(v);",
            "}",
            "",
            "bool truth(const Value& v) {",
            "    if (holds_alternative<bool>(v))",
            "        return get<bool>(v);",
            "    if (holds_alternative<int64_t>(v))",
            "        return get<int64_t>(v) != 0;",
            "    return get<double>(v) != 0.0;",
            "}",
            "",
            "Value pop(vector<Value>& s) {",
            "    if (s.empty())",
            '        throw runtime_error("Stack underflow");',
            "    Value v = s.back();",
            "    s.pop_back();",
            "    return v;",
            "}",
            "",
            "pair<Value, Value> pop2(vector<Value>& s) {",
            "    Value b = pop(s);",
            "    Value a = pop(s);",
            "    return {a, b};",
            "}",
            "",
            "int64_t floor_div_int(int64_t a, int64_t b) {",
            '    if (b == 0) throw runtime_error("Division by zero");',
            "    if (a == numeric_limits<int64_t>::min() && b == -1)",
            '        throw runtime_error("Integer overflow");',
            "    int64_t q = a / b;",
            "    int64_t r = a % b;",
            "    if (r != 0 && ((r < 0) != (b < 0))) --q;",
            "    return q;",
            "}",
            "",
            "int64_t mod_int(int64_t a, int64_t b) {",
            '    if (b == 0) throw runtime_error("Modulo by zero");',
            "    if (a == numeric_limits<int64_t>::min() && b == -1)",
            "        return 0;",
            "    int64_t r = a % b;",
            "    if (r != 0 && ((r < 0) != (b < 0))) r += b;",
            "    return r;",
            "}",
            "",
            "double floor_div_float(double a, double b) {",
            '    if (b == 0.0) throw runtime_error("Division by zero");',
            "    return floor(a / b);",
            "}",
            "",
            "double mod_float(double a, double b) {",
            '    if (b == 0.0) throw runtime_error("Modulo by zero");',
            "    double r = fmod(a, b);",
            "    if (r != 0.0 && ((r < 0.0) != (b < 0.0))) r += b;",
            "    return r;",
            "}",
            "",
            "int main() {",
            "    cout << setprecision(17);",
            "    vector<Value> stack;",
            "    unordered_map<string, Value> variables;",
            "",
        ]

        # Constant pool
        lines.append("    vector<Value> constants = {")

        for constant in constants:
            if constant.data_type == "int":
                value = str(constant.value)
                lines.append(
                    f"        Value{{static_cast<int64_t>({value})}},"
                )

            elif constant.data_type == "float":
                value = repr(constant.value)
                lines.append(
                    f"        Value{{static_cast<double>({value})}},"
                )

            elif constant.data_type == "bool":
                value = "true" if constant.value else "false"
                lines.append(f"        Value{{{value}}},")

            else:
                raise CppGeneratorError(
                    f"Unsupported constant type: {constant.data_type}"
                )

        lines.extend([
            "    };",
            "",
            "    vector<string> names = {",
        ])

        for name in names:
            escaped = (
                name.replace("\\", "\\\\")
                    .replace('"', '\\"')
            )
            lines.append(f'        "{escaped}",')

        lines.extend([
            "    };",
            "",
            "    struct Instruction { int opcode; int operand; };",
            "    vector<Instruction> code = {",
        ])

        for instruction in instructions:
            lines.append(
                f"        {{{int(instruction.opcode)}, "
                f"{instruction.operand}}},"
            )

        lines.extend([
            "    };",
            "",
            "    size_t pc = 0;",
            "    while (pc < code.size()) {",
            "        Instruction ins = code[pc++];",
            "        int op = ins.opcode;",
            "        int arg = ins.operand;",
            "        Value a, b;",
            "        pair<Value, Value> pair_values;",
            "",
            "        switch (op) {",
        ])

        def case(opcode, body):
            lines.append(f"        case {int(opcode)}: {{")
            for statement in body:
                lines.append("            " + statement)
            lines.append("            break;")
            lines.append("        }")

        # HALT
        case(Opcode.HALT, ["return 0;"])

        # POP
        case(Opcode.POP, ["pop(stack);"])

        # Constant loading
        for opcode in (
            Opcode.LOAD_INT,
            Opcode.LOAD_FLOAT,
            Opcode.LOAD_BOOL,
        ):
            case(opcode, [
                'if (arg < 0 || static_cast<size_t>(arg) >= constants.size())',
                '    throw runtime_error("Invalid constant index");',
                "stack.push_back(constants[arg]);",
            ])

        # Variables
        case(Opcode.LOAD_VAR, [
            'if (arg < 0 || static_cast<size_t>(arg) >= names.size())',
            '    throw runtime_error("Invalid variable index");',
            "string name = names[arg];",
            'if (!variables.count(name))',
            '    throw runtime_error("Undefined variable: " + name);',
            "stack.push_back(variables[name]);",
        ])

        case(Opcode.STORE_VAR, [
            'if (arg < 0 || static_cast<size_t>(arg) >= names.size())',
            '    throw runtime_error("Invalid variable index");',
            "variables[names[arg]] = pop(stack);",
        ])

        # Arithmetic
        arithmetic = {
            Opcode.ADD_INT: "number(a) + number(b)",
            Opcode.SUB_INT: "number(a) - number(b)",
            Opcode.MUL_INT: "number(a) * number(b)",
            Opcode.DIV_INT: "number(a) / number(b)",
            Opcode.FLOOR_DIV_INT: "floor(number(a) / number(b))",
            Opcode.MOD_INT: "number(a) - floor(number(a) / number(b)) * number(b)",
            Opcode.POWER_INT: "pow(number(a), number(b))",

            Opcode.ADD_FLOAT: "number(a) + number(b)",
            Opcode.SUB_FLOAT: "number(a) - number(b)",
            Opcode.MUL_FLOAT: "number(a) * number(b)",
            Opcode.DIV_FLOAT: "number(a) / number(b)",
            Opcode.FLOOR_DIV_FLOAT: "floor_div_float(number(a), number(b))",
            Opcode.MOD_FLOAT: "mod_float(number(a), number(b))",
            Opcode.POWER_FLOAT: "pow(number(a), number(b))",
        }

        for opcode, expression in arithmetic.items():
            body = [
                "pair_values = pop2(stack);",
                "a = pair_values.first;",
                "b = pair_values.second;",
            ]

            if opcode in (
                Opcode.DIV_INT,
                Opcode.DIV_FLOAT,
                Opcode.FLOOR_DIV_INT,
                Opcode.FLOOR_DIV_FLOAT,
                Opcode.MOD_INT,
                Opcode.MOD_FLOAT,
            ):
                body.append(
                    'if (number(b) == 0.0) '
                    'throw runtime_error("Division by zero");'
                )

            body.append(
                f"stack.push_back(Value{{{expression}}});"
            )

            case(opcode, body)

        # Comparisons
        comparisons = {
            Opcode.CMP_EQ: "number(a) == number(b)",
            Opcode.CMP_NE: "number(a) != number(b)",
            Opcode.CMP_LT: "number(a) < number(b)",
            Opcode.CMP_GT: "number(a) > number(b)",
            Opcode.CMP_LE: "number(a) <= number(b)",
            Opcode.CMP_GE: "number(a) >= number(b)",
        }

        for opcode, expression in comparisons.items():
            case(opcode, [
                "pair_values = pop2(stack);",
                "a = pair_values.first;",
                "b = pair_values.second;",
                f"stack.push_back(Value{{{expression}}});",
            ])

        # Logical operations
        case(Opcode.TO_BOOL, [
            "a = pop(stack);",
            "stack.push_back(Value{truth(a)});",
        ])

        case(Opcode.LOGICAL_NOT, [
            "a = pop(stack);",
            "stack.push_back(Value{!truth(a)});",
        ])

        case(Opcode.LOGICAL_AND, [
            "pair_values = pop2(stack);",
            "stack.push_back(Value{truth(pair_values.first) && truth(pair_values.second)});",
        ])

        case(Opcode.LOGICAL_OR, [
            "pair_values = pop2(stack);",
            "stack.push_back(Value{truth(pair_values.first) || truth(pair_values.second)});",
        ])

        # Bitwise operations
        for opcode, expression in {
            Opcode.BIT_AND: "integer(a) & integer(b)",
            Opcode.BIT_OR: "integer(a) | integer(b)",
            Opcode.BIT_XOR: "integer(a) ^ integer(b)",
            Opcode.LSHIFT: "integer(a) << integer(b)",
            Opcode.RSHIFT: "integer(a) >> integer(b)",
        }.items():
            body = [
                "pair_values = pop2(stack);",
                "a = pair_values.first;",
                "b = pair_values.second;",
                'if (integer(b) < 0) throw runtime_error("Negative shift count");'
                if opcode in (Opcode.LSHIFT, Opcode.RSHIFT)
                else "",
                f"stack.push_back(Value{{static_cast<int64_t>({expression})}});",
            ]
            case(opcode, [line for line in body if line])

        case(Opcode.BIT_NOT, [
            "a = pop(stack);",
            "stack.push_back(Value{static_cast<int64_t>(~integer(a))});",
        ])

        # Unary operations
        case(Opcode.NEG, [
            "a = pop(stack);",
            "if (holds_alternative<int64_t>(a))",
            "    stack.push_back(Value{-get<int64_t>(a)});",
            "else if (holds_alternative<double>(a))",
            "    stack.push_back(Value{-get<double>(a)});",
            'else throw runtime_error("Unary minus requires a number");',
        ])

        case(Opcode.POS, [
            "a = pop(stack);",
            "if (!holds_alternative<int64_t>(a) && !holds_alternative<double>(a))",
            '    throw runtime_error("Unary plus requires a number");',
            "stack.push_back(a);",
        ])

        # Type conversions
        case(Opcode.INT_TO_FLOAT, [
            "a = pop(stack);",
            "stack.push_back(Value{number(a)});",
        ])

        case(Opcode.FLOAT_TO_INT, [
            "a = pop(stack);",
            "stack.push_back(Value{static_cast<int64_t>(number(a))});",
        ])

        # Jumps use absolute instruction indexes.
        case(Opcode.JUMP, [
            'if (arg < 0 || static_cast<size_t>(arg) >= code.size())',
            '    throw runtime_error("Invalid jump target");',
            "pc = static_cast<size_t>(arg);",
        ])

        case(Opcode.JUMP_IF_FALSE, [
            "a = pop(stack);",
            "if (!truth(a)) {",
            '    if (arg < 0 || static_cast<size_t>(arg) >= code.size())',
            '        throw runtime_error("Invalid jump target");',
            "    pc = static_cast<size_t>(arg);",
            "}",
        ])

        case(Opcode.JUMP_IF_TRUE, [
            "a = pop(stack);",
            "if (truth(a)) {",
            '    if (arg < 0 || static_cast<size_t>(arg) >= code.size())',
            '        throw runtime_error("Invalid jump target");',
            "    pc = static_cast<size_t>(arg);",
            "}",
        ])

        # Output
        case(Opcode.PRINT_INT, [
            "a = pop(stack);",
            "cout << integer(a) << endl;",
        ])

        case(Opcode.PRINT_FLOAT, [
            "a = pop(stack);",
            "cout << number(a) << endl;",
        ])

        case(Opcode.PRINT_BOOL, [
            "a = pop(stack);",
            'cout << (truth(a) ? "True" : "False") << endl;',
        ])

        lines.extend([
            "        default:",
            '            throw runtime_error("Unknown opcode: " + to_string(op));',
            "        }",
            "    }",
            "",
            "    return 0;",
            "}",
        ])

        return "\n".join(lines)

    def save(self, filename="generated/generated.cpp"):
        from pathlib import Path

        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)

        code = self.generate()

        path.write_text(
            code,
            encoding="utf-8"
        )

        return str(path)


def generate_cpp(program, filename=None):
    generator = CppGenerator(program)

    if filename:
        return generator.save(filename)

    return generator.generate()
