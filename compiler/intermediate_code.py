from dataclasses import dataclass, field


@dataclass
class IRInstruction:
    operation: str
    operand: int = 0


@dataclass
class IRProgram:
    instructions: list = field(default_factory=list)
    constants: list = field(default_factory=list)
    variables: list = field(default_factory=list)


class IRGenerator:

    def __init__(self):

        self.program = IRProgram()

    def emit(self, operation, operand=0):

        self.program.instructions.append(
            IRInstruction(operation, operand)
        )

    def add_constant(self, value):

        if value not in self.program.constants:
            self.program.constants.append(value)

        return self.program.constants.index(value)

    def add_variable(self, name):

        if name not in self.program.variables:
            self.program.variables.append(name)

        return self.program.variables.index(name)

    def generate_expression(self, node):

        if node.operation == "CONST":

            self.emit(
                "LOAD_CONST",
                self.add_constant(node.value)
            )

        elif node.operation == "VAR":

            self.emit(
                "LOAD_VAR",
                self.add_variable(node.value)
            )

        elif node.operation == "NEG":

            self.generate_expression(node.operand)
            self.emit("NEG")

        else:

            self.generate_expression(node.left)
            self.generate_expression(node.right)

            self.emit(node.operation)

    def generate(self, statements):

        for statement in statements:

            if statement[0] == "ASSIGN":

                _, name, expression = statement

                self.generate_expression(expression)

                self.emit(
                    "STORE_VAR",
                    self.add_variable(name)
                )

            elif statement[0] == "PRINT":

                self.generate_expression(statement[1])

                self.emit("PRINT")

        self.emit("HALT")

        return self.program