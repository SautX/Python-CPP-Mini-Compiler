
import sys
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont, QColor
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QPushButton,
    QLabel,
    QTabWidget,
    QFileDialog,
    QMessageBox,
    QStatusBar,
    QToolBar,
    QFrame,
    QPlainTextEdit,
    QGroupBox,
    QGridLayout
)

from gui.code_editor import CodeEditor
from gui.terminal import Terminal
from gui.bytecode_viewer import BytecodeViewer
from gui.alu_dashboard import ALUDashboard
from gui.memory_viewer import MemoryViewer


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "PYTHON → C++ | 24-BIT MINI COMPILER"
        )

        self.resize(1500, 900)
        self.setMinimumSize(1100, 700)

        self.project_dir = Path.cwd()
        self.current_file = None
        self.current_program = None
        self.generated_cpp = None

        self.create_widgets()
        self.create_menu()
        self.create_toolbar()
        self.create_layout()
        self.create_status_bar()
        self.load_style()
        self.load_default_code()

    # --------------------------------------------------
    # WIDGET CREATION
    # --------------------------------------------------

    def create_widgets(self):

        self.editor = CodeEditor()
        self.terminal = Terminal()
        self.bytecode_viewer = BytecodeViewer()
        self.alu_dashboard = ALUDashboard()
        self.memory_viewer = MemoryViewer()

        self.cpp_viewer = QPlainTextEdit()
        self.cpp_viewer.setReadOnly(True)
        self.cpp_viewer.setPlaceholderText(
            "Generated C++ code will appear here..."
        )
        self.cpp_viewer.setFont(QFont("Consolas", 11))

        self.ir_viewer = QPlainTextEdit()
        self.ir_viewer.setReadOnly(True)
        self.ir_viewer.setPlaceholderText(
            "Intermediate representation will appear here..."
        )
        self.ir_viewer.setFont(QFont("Consolas", 11))

        self.project_label = QLabel("PROJECT EXPLORER")
        self.project_label.setObjectName("sectionTitle")

        self.project_info = QLabel(
            "Python-to-C++ Mini Compiler\n"
            "Architecture: 24-bit Virtual CPU\n"
            "Backend: C++17"
        )

    # --------------------------------------------------
    # MENU BAR
    # --------------------------------------------------

    def create_menu(self):

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        build_menu = menu_bar.addMenu("Build")
        help_menu = menu_bar.addMenu("Help")

        new_action = QAction("New File", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)

        open_action = QAction("Open File", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)

        save_action = QAction("Save File", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        compile_action = QAction("Compile", self)
        compile_action.setShortcut("F5")
        compile_action.triggered.connect(self.compile_code)

        run_action = QAction("Run", self)
        run_action.setShortcut("F6")
        run_action.triggered.connect(self.run_code)

        build_menu.addAction(compile_action)
        build_menu.addAction(run_action)

        about_action = QAction("About Compiler", self)
        about_action.triggered.connect(self.show_about)

        help_menu.addAction(about_action)

        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self.editor.undo)

        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.triggered.connect(self.editor.redo)

        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)

    # --------------------------------------------------
    # TOOLBAR
    # --------------------------------------------------

    def create_toolbar(self):

        toolbar = QToolBar("Compiler Toolbar")
        toolbar.setMovable(False)

        self.addToolBar(toolbar)

        new_button = QPushButton("NEW")
        open_button = QPushButton("OPEN")
        save_button = QPushButton("SAVE")
        compile_button = QPushButton("▶ COMPILE")
        run_button = QPushButton("▶ RUN")
        clear_button = QPushButton("CLEAR TERMINAL")

        new_button.clicked.connect(self.new_file)
        open_button.clicked.connect(self.open_file)
        save_button.clicked.connect(self.save_file)
        compile_button.clicked.connect(self.compile_code)
        run_button.clicked.connect(self.run_code)
        clear_button.clicked.connect(self.clear_terminal)

        for button in [
            new_button,
            open_button,
            save_button,
            compile_button,
            run_button,
            clear_button
        ]:
            toolbar.addWidget(button)

        toolbar.addSeparator()

        toolbar.addWidget(
            QLabel("  COMPILER STATUS: ")
        )

        self.status_indicator = QLabel("● READY")
        self.status_indicator.setObjectName("readyStatus")

        toolbar.addWidget(self.status_indicator)

    # --------------------------------------------------
    # MAIN WINDOW LAYOUT
    # --------------------------------------------------

    def create_layout(self):

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Header
        header = QLabel(
            "⚡ PYTHON → C++ MINI COMPILER"
            "     |     24-BIT VIRTUAL PROCESSOR"
        )

        header.setObjectName("header")
        header.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(header)

        # Main horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal)

        # Project explorer
        project_panel = QFrame()
        project_panel.setObjectName("panel")

        project_layout = QVBoxLayout(project_panel)

        project_layout.addWidget(self.project_label)
        project_layout.addWidget(self.project_info)

        project_layout.addWidget(QLabel("WORKSPACE"))
        project_layout.addWidget(
            QLabel(
                "📁 Python_CPP_Mini_Compiler\n"
                "   📁 compiler\n"
                "   📁 architecture\n"
                "   📁 examples\n"
                "   📁 generated\n"
                "   📁 output\n"
                "   📁 gui\n"
                "   📁 tests"
            )
        )

        project_layout.addStretch()

        # Editor and output tabs
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)

        center_layout.addWidget(
            QLabel("SOURCE CODE EDITOR")
        )

        self.editor_tabs = QTabWidget()
        self.editor_tabs.addTab(
            self.editor,
            "Python Source"
        )

        center_layout.addWidget(self.editor_tabs, 4)

        # Output tabs
        self.output_tabs = QTabWidget()

        self.output_tabs.addTab(
            self.bytecode_viewer,
            "24-BIT BYTECODE"
        )

        self.output_tabs.addTab(
            self.cpp_viewer,
            "GENERATED C++"
        )

        self.output_tabs.addTab(
            self.ir_viewer,
            "INTERMEDIATE CODE"
        )

        self.output_tabs.addTab(
            self.alu_dashboard,
            "ALU DASHBOARD"
        )

        self.output_tabs.addTab(
            self.memory_viewer,
            "MEMORY / REGISTERS"
        )

        center_layout.addWidget(self.output_tabs, 3)

        main_splitter.addWidget(project_panel)
        main_splitter.addWidget(center_panel)

        main_splitter.setSizes([240, 1200])

        main_layout.addWidget(main_splitter, 5)

        # Terminal
        main_layout.addWidget(
            QLabel("▸ COMPILER TERMINAL")
        )

        main_layout.addWidget(self.terminal, 2)

    # --------------------------------------------------
    # STATUS BAR
    # --------------------------------------------------

    def create_status_bar(self):

        status = QStatusBar()
        self.setStatusBar(status)

        status.showMessage(
            "READY | Python Frontend | Custom Bytecode | C++ Backend"
        )

    # --------------------------------------------------
    # DEFAULT SOURCE CODE
    # --------------------------------------------------

    def load_default_code(self):

        code = """# Python to C++ Mini Compiler
# 24-bit instruction architecture

a = 10
b = 20

c = a + b * 2

print(c)

x = (c - 5) % 7

print(x)

y = -15

print(y)
"""

        self.editor.setPlainText(code)

    # --------------------------------------------------
    # FILE OPERATIONS
    # --------------------------------------------------

    def new_file(self):

        self.editor.clear()
        self.current_file = None

        self.terminal.append_text(
            "[INFO] New source file created."
        )

    def open_file(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Python File",
            "",
            "Python Files (*.py);;All Files (*)"
        )

        if not filename:
            return

        try:
            self.current_file = Path(filename)

            source = self.current_file.read_text(
                encoding="utf-8"
            )

            self.editor.setPlainText(source)

            self.terminal.append_text(
                f"[OPENED] {filename}"
            )

        except OSError as error:
            self.show_error(str(error))

    def save_file(self):

        if self.current_file is None:

            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Python File",
                "program.py",
                "Python Files (*.py)"
            )

            if not filename:
                return

            self.current_file = Path(filename)

        try:
            self.current_file.write_text(
                self.editor.toPlainText(),
                encoding="utf-8"
            )

            self.terminal.append_text(
                f"[SAVED] {self.current_file}"
            )

        except OSError as error:
            self.show_error(str(error))

    # --------------------------------------------------
    # COMPILER FUNCTION
    # --------------------------------------------------

    def compile_code(self):

        source = self.editor.toPlainText()

        if not source.strip():
            self.show_error("Source code is empty.")
            return

        self.status_indicator.setText("● COMPILING")
        self.terminal.append_text(
            "\n========== COMPILATION STARTED =========="
        )

        try:
            from compiler.frontend import (
                compile_source_to_bytecode
            )

            from compiler.backend import generate_cpp

            self.project_dir = Path.cwd()

            generated_dir = self.project_dir / "generated"
            generated_dir.mkdir(exist_ok=True)

            # Step 1: Python source to custom bytecode
            self.terminal.append_text(
                "[1/4] Analysing Python source..."
            )

            self.current_program = (
                compile_source_to_bytecode(source)
            )

            self.terminal.append_text(
                "[2/4] Generating custom 24-bit bytecode..."
            )

            # Step 2: Display bytecode
            self.bytecode_viewer.display_program(
                self.current_program
            )

            # Step 3: Generate C++
            self.terminal.append_text(
                "[3/4] Generating C++ code..."
            )

            cpp_code = generate_cpp(
                self.current_program
            )

            self.generated_cpp = cpp_code

            cpp_path = generated_dir / "generated.cpp"

            cpp_path.write_text(
                cpp_code,
                encoding="utf-8"
            )

            self.cpp_viewer.setPlainText(cpp_code)

            # Step 4: Save bytecode
            self.save_binary_bytecode(
                self.current_program,
                generated_dir / "bytecode.bin"
            )

            self.terminal.append_text(
                "[4/4] Saving generated files..."
            )

            self.terminal.append_text(
                "[SUCCESS] Compilation completed."
            )

            self.terminal.append_text(
                f"[OUTPUT] {cpp_path}"
            )

            self.status_indicator.setText("● COMPILED")
            self.statusBar().showMessage(
                "Compilation successful"
            )

            self.output_tabs.setCurrentIndex(0)

        except Exception as error:

            self.status_indicator.setText("● ERROR")

            self.terminal.append_text(
                f"[COMPILATION ERROR] {error}"
            )

            self.show_error(str(error))

    # --------------------------------------------------
    # BINARY BYTECODE OUTPUT
    # --------------------------------------------------

    def save_binary_bytecode(self, program, path):

        with open(path, "wb") as file:

            for instruction in program.instructions:

                file.write(
                    instruction.to_bytes(
                        3,
                        byteorder="big"
                    )
                )

    # --------------------------------------------------
    # RUN GENERATED EXECUTABLE
    # --------------------------------------------------

    def run_code(self):

        if self.current_program is None:
            self.compile_code()

        if self.current_program is None:
            return

        cpp_path = (
            self.project_dir /
            "generated" /
            "generated.cpp"
        )

        output_dir = self.project_dir / "output"
        output_dir.mkdir(exist_ok=True)

        executable = output_dir / "executable.exe"

        self.terminal.append_text(
            "\n========== C++ BUILD STARTED =========="
        )

        try:

            build = subprocess.run(
                [
                    "g++",
                    "-std=c++17",
                    str(cpp_path),
                    "-o",
                    str(executable)
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            if build.returncode != 0:

                self.terminal.append_text(
                    "[C++ BUILD FAILED]"
                )

                self.terminal.append_text(build.stderr)

                self.status_indicator.setText("● ERROR")
                return

            self.terminal.append_text(
                "[SUCCESS] C++ executable created."
            )

            self.terminal.append_text(
                "\n========== PROGRAM OUTPUT =========="
            )

            result = subprocess.run(
                [str(executable)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.project_dir)
            )

            self.terminal.append_text(result.stdout)

            if result.stderr:
                self.terminal.append_text(result.stderr)

            self.terminal.append_text(
                "\n========== EXECUTION FINISHED =========="
            )

            self.status_indicator.setText("● EXECUTED")

        except FileNotFoundError:

            self.terminal.append_text(
                "[ERROR] GCC was not found."
            )

            self.terminal.append_text(
                "Install MinGW-w64 and add g++ to PATH."
            )

        except subprocess.TimeoutExpired:

            self.terminal.append_text(
                "[ERROR] Program execution timed out."
            )

        except Exception as error:

            self.terminal.append_text(
                f"[RUN ERROR] {error}"
            )

    # --------------------------------------------------
    # TERMINAL
    # --------------------------------------------------

    def clear_terminal(self):

        self.terminal.clear()

        self.terminal.append_text(
            "PYTHON → C++ MINI COMPILER\n"
            "24-BIT VIRTUAL PROCESSOR READY\n"
            "----------------------------------"
        )

    # --------------------------------------------------
    # STYLE
    # --------------------------------------------------

    def load_style(self):

        style_path = (
            Path(__file__).parent / "styles.qss"
        )

        if style_path.exists():

            self.setStyleSheet(
                style_path.read_text(
                    encoding="utf-8"
                )
            )

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

    def show_error(self, message):

        QMessageBox.critical(
            self,
            "Compiler Error",
            str(message)
        )

    def show_about(self):

        QMessageBox.about(
            self,
            "About Mini Compiler",
            """
            PYTHON TO C++ MINI COMPILER

            Version: 1.0

            Architecture:
            Custom 24-bit Instruction Set

            Frontend:
            Python Source Processing

            Backend:
            C++17 Code Generation

            Interface:
            PySide6

            Project:
            Educational Compiler and
            Virtual Processor Simulation
            """
        )
