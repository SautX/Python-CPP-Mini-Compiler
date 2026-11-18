
import sys
import argparse
import shutil
import subprocess

from pathlib import Path

from compiler.frontend import compile_source_to_bytecode
from compiler.bytecode import format_program
from compiler.backend import generate_cpp


# ==========================================
# PYTHON TO C++ MINI COMPILER
# ==========================================

class MiniCompilerApp:

    def __init__(self):
        self.output_dir = Path("generated")
        self.output_dir.mkdir(exist_ok=True)

    # --------------------------------------
    # Read Python Source Code
    # --------------------------------------

    def read_source(self, filename):

        path = Path(filename)

        if not path.exists():
            raise FileNotFoundError(
                f"Source file not found: {filename}"
            )

        return path.read_text(encoding="utf-8")

    # --------------------------------------
    # Generate Custom Bytecode
    # --------------------------------------

    def generate_bytecode(self, source):

        print("\n[1] COMPILING PYTHON SOURCE...")

        program = compile_source_to_bytecode(source)

        print("\n[2] GENERATED 24-BIT BYTECODE")

        print(format_program(program))

        return program

    # --------------------------------------
    # Generate C++ Code
    # --------------------------------------

    def generate_cpp_code(self, program):

        print("\n[3] GENERATING C++ CODE...")

        cpp_code = generate_cpp(program)

        cpp_file = self.output_dir / "generated.cpp"

        cpp_file.write_text(
            cpp_code,
            encoding="utf-8"
        )

        print(f"C++ file generated: {cpp_file}")

        return cpp_file

    # --------------------------------------
    # Compile C++ Code
    # --------------------------------------

    def compile_cpp(self, cpp_file):

        compiler = shutil.which("g++")

        if compiler is None:
            print("\nG++ compiler not found!")
            print("Install MinGW-w64 or GCC.")
            return None

        executable = self.output_dir / (
            "executable.exe"
            if sys.platform == "win32"
            else "executable"
        )

        print("\n[4] COMPILING C++ BACKEND...")

        result = subprocess.run(
            [
                compiler,
                "-std=c++17",
                str(cpp_file),
                "-o",
                str(executable)
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:

            print("\nC++ COMPILATION ERROR")
            print(result.stderr)

            return None

        print("Compilation successful!")

        return executable

    # --------------------------------------
    # Execute Program
    # --------------------------------------

    def execute_program(self, executable):

        if executable is None:
            return

        print("\n[5] EXECUTING PROGRAM")

        result = subprocess.run(
            [str(executable)],
            capture_output=True,
            text=True
        )

        print("\n========== OUTPUT ==========")

        print(result.stdout, end="")

        if result.stderr:
            print("\nERROR:")
            print(result.stderr)

        print("============================")

    # --------------------------------------
    # Complete Compiler Pipeline
    # --------------------------------------

    def run(self, filename):

        try:

            source = self.read_source(filename)

            program = self.generate_bytecode(source)

            cpp_file = self.generate_cpp_code(program)

            executable = self.compile_cpp(cpp_file)

            self.execute_program(executable)

        except Exception as error:

            print("\nCOMPILER ERROR:")
            print(error)


# ==========================================
# MAIN FUNCTION
# ==========================================

def main():

    parser = argparse.ArgumentParser(
        description="Python to C++ Mini Compiler"
    )

    parser.add_argument(
        "source",
        nargs="?",
        default="examples/sample.py",
        help="Python source file"
    )

    args = parser.parse_args()

    app = MiniCompilerApp()

    print("=" * 50)
    print("       PYTHON TO C++ MINI COMPILER")
    print("       CUSTOM 24-BIT INSTRUCTION SET")
    print("=" * 50)

    app.run(args.source)


if __name__ == "__main__":
    main()
