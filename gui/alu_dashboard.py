from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGridLayout,
    QGroupBox
)


class ALUDashboard(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("ARITHMETIC LOGIC UNIT")
        layout.addWidget(title)

        group = QGroupBox("PROCESSOR FLAGS")
        grid = QGridLayout(group)

        self.zero = QLabel("ZERO: 0")
        self.negative = QLabel("NEGATIVE: 0")
        self.carry = QLabel("CARRY: 0")
        self.overflow = QLabel("OVERFLOW: 0")

        grid.addWidget(self.zero, 0, 0)
        grid.addWidget(self.negative, 0, 1)
        grid.addWidget(self.carry, 1, 0)
        grid.addWidget(self.overflow, 1, 1)

        layout.addWidget(group)

        self.operation = QLabel("OPERATION: IDLE")
        self.result = QLabel("ALU RESULT: 0")

        layout.addWidget(self.operation)
        layout.addWidget(self.result)

        layout.addStretch()

    def update_alu(self, operation, result, flags=None):

        self.operation.setText(f"OPERATION: {operation}")
        self.result.setText(f"ALU RESULT: {result}")

        if flags is not None:
            self.zero.setText(f"ZERO: {flags.get('zero', 0)}")
            self.negative.setText(
                f"NEGATIVE: {flags.get('negative', 0)}"
            )
            self.carry.setText(f"CARRY: {flags.get('carry', 0)}")
            self.overflow.setText(
                f"OVERFLOW: {flags.get('overflow', 0)}"
            )