from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem
)


class MemoryViewer(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 2)

        self.table.setHorizontalHeaderLabels([
            "REGISTER / MEMORY",
            "VALUE"
        ])

        layout.addWidget(self.table)

    def update_memory(self, memory_data):

        self.table.setRowCount(len(memory_data))

        for row, (name, value) in enumerate(memory_data.items()):

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(str(name))
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(str(value))
            )