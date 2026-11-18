from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QFont, QColor, QTextCharFormat


class CodeEditor(QPlainTextEdit):

    def __init__(self):
        super().__init__()

        self.setPlaceholderText(
            "# Write your Python program here\n\n"
            "a = 10\n"
            "b = 20\n"
            "c = a + b * 2\n"
            "print(c)\n"
        )

        self.setFont(QFont("Consolas", 12))
        self.setTabStopDistance(32)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)