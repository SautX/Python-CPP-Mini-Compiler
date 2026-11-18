from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPlainTextEdit
)

from PySide6.QtGui import QFont


class BytecodeViewer(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.display = QPlainTextEdit()
        self.display.setReadOnly(True)
        self.display.setFont(QFont("Consolas", 11))

        layout.addWidget(self.display)

    def display_program(self, program):

        self.display.clear()

        self.display.appendPlainText(
            "ADDRESS     OPCODE     OPERAND     24-BIT INSTRUCTION"
        )

        self.display.appendPlainText("-" * 65)

        for index, instruction in enumerate(program.instructions):

            encoded = instruction.encode()

            self.display.appendPlainText(
                f"{index:04X}        "
                f"{instruction.opcode:02X}         "
                f"{instruction.operand:04X}        "
                f"{encoded:024b}"
            )