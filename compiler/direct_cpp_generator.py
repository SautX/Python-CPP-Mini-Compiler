
import ast
import math


class DirectCppGenerationError(Exception):
    """Raised when Python code cannot be translated to supported C++."""


class DirectCppGenerator:
    """
    Directly translates the supported Python AST subset into C++.

    Supported:
      - int, float and bool variables
      - assignments
      - arithmetic, comparison and logical expressions
      - bitwise and shift expressions
      - unary expressions
      - print()
      - multiple statements

    This generator uses Python's built-in AST for reliable syntax parsing.
    It does not execute the Python source.
    """

    BINARY_OPERATORS = {
        ast.Add: "+",
        ast.Sub: "-",
        ast.Mult: "*",
        ast.Div: "/",
        ast.FloorDiv: "/",
        ast.Mod: "%",
        ast.Pow: "**",
        ast.BitAnd: "&",
        ast.BitOr: "|",
        ast.BitXor: "^",
        ast.LShift: "<<",
        ast.RShift: ">>",
    }

    COMPARISON_OPERATORS = {
        ast.Eq: "==",
        ast.NotEq: "!=",
        ast.Lt: "<",
        ast.LtE: "<=",
        ast.Gt: ">",
        ast.GtE: ">=",
    }

    UNARY_OPERATORS = {
        ast.UAdd: "+",
        ast.USub: "-",
        ast.Not: "!",
        ast.Invert: "~",
    }

    def __init__(self):
        self.declared_variables = set()
        self.variable_types = {}
        self.lines = []

    def _cpp_type(self, python_type):
        mapping = {
            "int": "long long",
            "float": "double",
            "bool": "bool",
        }

        if python_type not in mapping:
            raise DirectCppGenerationError(
                f"Unsupported variable type: {python_type}"
            )

        return mapping[python_type]

    def _infer_type(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return "bool"
            if isinstance(node.value, int):
                return "int"
            if isinstance(node.value, float):
                return "float"

        if isinstance(node, ast.Name):
            if node.id not in self.variable_types:
                raise DirectCppGenerationError(
                    f"Variable '{node.id}' used before assignment."
                )
            return self.variable_types[node.id]

        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.Not):
                return "bool"
            return self._infer_type(node.operand)

        if isinstance(node, ast.BoolOp):
            return "bool"

        if isinstance(node, ast.Compare):
            return "bool"

        if isinstance(node, ast.BinOp):
            left_type = self._infer_type(node.left)
            right_type = self._infer_type(node.right)

            if isinstance(node.op, (ast.BitAnd, ast.BitOr,
                                    ast.BitXor, ast.LShift,
                                    ast.RShift)):
                if left_type != "int" or right_type != "int":
                    raise DirectCppGenerationError(
                        "Bitwise operations require integer operands."
                    )
                return "int"

            if isinstance(node.op, ast.Div):
                return "float"

            if "float" in (left_type, right_type):
                return "float"

            return "int"

        raise DirectCppGenerationError(
            f"Unsupported expression: {type(node).__name__}"
        )

    def _expression(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return "true" if node.value else "false"

            if isinstance(node.value, int):
                return str(node.value)

            if isinstance(node.value, float):
                if not math.isfinite(node.value):
                    raise DirectCppGenerationError(
                        "Non-finite float literals are not supported."
                    )
                return repr(node.value)

            raise DirectCppGenerationError(
                "Only integer, float and Boolean literals are supported."
            )

        if isinstance(node, ast.Name):
            if node.id not in self.declared_variables:
                raise DirectCppGenerationError(
                    f"Variable '{node.id}' used before assignment."
                )
            return node.id

        if isinstance(node, ast.BinOp):
            left = self._expression(node.left)
            right = self._expression(node.right)

            if isinstance(node.op, ast.Pow):
                return f"pow({left}, {right})"

            operator = self.BINARY_OPERATORS.get(type(node.op))

            if operator is None:
                raise DirectCppGenerationError(
                    f"Unsupported binary operator: {type(node.op).__name__}"
                )

            return f"({left} {operator} {right})"

        if isinstance(node, ast.UnaryOp):
            operator = self.UNARY_OPERATORS.get(type(node.op))

            if operator is None:
                raise DirectCppGenerationError(
                    "Unsupported unary operator."
                )

            return f"({operator}{self._expression(node.operand)})"

        if isinstance(node, ast.BoolOp):
            operator = "&&" if isinstance(node.op, ast.And) else "||"
            values = [self._expression(value) for value in node.values]
            return "(" + f" {operator} ".join(values) + ")"

        if isinstance(node, ast.Compare):
            if len(node.ops) != 1:
                raise DirectCppGenerationError(
                    "Chained comparisons are not supported yet."
                )

            operator = self.COMPARISON_OPERATORS.get(
                type(node.ops[0])
            )

            if operator is None:
                raise DirectCppGenerationError(
                    "Unsupported comparison operator."
                )

            left = self._expression(node.left)
            right = self._expression(node.comparators[0])

            return f"({left} {operator} {right})"

        raise DirectCppGenerationError(
            f"Unsupported expression: {type(node).__name__}"
        )

    def _statement(self, node):
        if isinstance(node, ast.Assign):
            if len(node.targets) != 1:
                raise DirectCppGenerationError(
                    "Only single-variable assignments are supported."
                )

            target = node.targets[0]

            if not isinstance(target, ast.Name):
                raise DirectCppGenerationError(
                    "Only simple variable assignments are supported."
                )

            name = target.id
            value = self._expression(node.value)
            value_type = self._infer_type(node.value)

            if name not in self.declared_variables:
                cpp_type = self._cpp_type(value_type)
                self.lines.append(
                    f"    {cpp_type} {name} = {value};"
                )
                self.declared_variables.add(name)
                self.variable_types[name] = value_type
            else:
                existing_type = self.variable_types[name]

                if existing_type == "int" and value_type == "float":
                    raise DirectCppGenerationError(
                        f"Cannot assign float to existing int variable '{name}'."
                    )

                self.lines.append(f"    {name} = {value};")

                if existing_type == "float" and value_type == "int":
                    self.lines[-1] = (
                        f"    {name} = static_cast<double>({value});"
                    )

        elif isinstance(node, ast.Expr):
            if (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "print"
            ):
                if len(node.value.args) != 1 or node.value.keywords:
                    raise DirectCppGenerationError(
                        "print() currently supports exactly one argument."
                    )

                value_node = node.value.args[0]
                value = self._expression(value_node)
                self.lines.append(
                    f"    std::cout << {value} << std::endl;"
                )
            else:
                raise DirectCppGenerationError(
                    "Only print() expression statements are supported."
                )

        else:
            raise DirectCppGenerationError(
                f"Unsupported statement: {type(node).__name__}"
            )

    def generate(self, source):
        if not isinstance(source, str) or not source.strip():
            raise DirectCppGenerationError(
                "Python source code cannot be empty."
            )

        self.declared_variables = set()
        self.variable_types = {}
        self.lines = []

        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            raise DirectCppGenerationError(
                f"Python syntax error on line {exc.lineno}: {exc.msg}"
            ) from exc

        for statement in tree.body:
            self._statement(statement)

        output = [
            "#include <iostream>",
            "#include <cmath>",
            "",
            "int main() {",
            *self.lines,
            "",
            "    return 0;",
            "}",
        ]

        return "\n".join(output) + "\n"
