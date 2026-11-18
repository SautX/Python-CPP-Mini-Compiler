from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QFont


class Terminal(QPlainTextEdit):

    def __init__(self):
        super().__init__()

        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 10))

        self.append_text(
            "PYTHON → C++ MINI COMPILER\n"
            "24-BIT VIRTUAL PROCESSOR READY\n"
            "----------------------------------"
        )

    def append_text(self, text):
        self.appendPlainText(str(text))