
# compiler/backend.py

import os
import subprocess
from pathlib import Path

from .frontend import Frontend
from .intermediate_code import (
    IntermediateCodeGenerator,
    IntermediateCodeLowerer,
)
from .optimizer import BytecodeOptimizer
from .cpp_generator import CppGenerator
from .bytecode import BytecodeProgram


class BackendError(Exception):
    pass


class CompilerBackend:

    def __init__(self, compiler="g++"):
        self.compiler = compiler

        self.frontend = Frontend()
        self.ir_generator = IntermediateCodeGenerator()
        self.bytecode_lowerer = IntermediateCodeLowerer()

        self.program = None
        self.ir = None
        self.frontend_result = None
        self.cpp_code = None

    def compile_source(self, source, optimize=True):
        """
        Complete source-to-bytecode pipeline.

        Python source
          -> Frontend
          -> AST
          -> Intermediate representation
          -> 24-bit bytecode
          -> Optimizer
        """

        self.frontend_result = self.frontend.compile(source)

        if not self.frontend_result["success"]:
            raise BackendError(
                "Frontend error: "
                + self.frontend_result["error"]
            )

        ast = self.frontend_result["ast"]

        try:
            self.ir = self.ir_generator.compile(ast)

            self.program = self.bytecode_lowerer.lower(
                self.ir
            )

            if optimize:
                self.program = BytecodeOptimizer(
                    self.program
                ).optimize()

        except Exception as error:
            raise BackendError(
                f"Backend compilation failed: {error}"
            ) from error

        return self.program

    def generate_cpp(self, output_file="generated.cpp"):
        if self.program is None:
            raise BackendError(
                "Compile source before generating C++"
            )

        generator = CppGenerator(self.program)

        self.cpp_code = generator.generate()

        output_path = Path(output_file)
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path.write_text(
            self.cpp_code,
            encoding="utf-8"
        )

        return str(output_path)

    def compile_cpp(
        self,
        cpp_file="generated.cpp",
        executable="executable.exe",
        extra_flags=None,
    ):
        cpp_path = Path(cpp_file)

        if not cpp_path.exists():
            raise BackendError(
                f"C++ source file not found: {cpp_file}"
            )

        executable_path = Path(executable)
        executable_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        command = [
            self.compiler,
            "-std=c++17",
            "-O2",
            str(cpp_path),
            "-o",
            str(executable_path),
        ]

        if extra_flags:
            command[1:1] = list(extra_flags)

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
            )

        except FileNotFoundError as error:
            raise BackendError(
                f"C++ compiler not found: {self.compiler}. "
                "Install GCC and add its bin directory to PATH."
            ) from error

        if result.returncode != 0:
            raise BackendError(
                "C++ compilation failed:\n"
                + result.stderr
            )

        return {
            "success": True,
            "executable": str(executable_path),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": command,
        }

    def run_executable(self, executable="executable.exe"):
        executable_path = Path(executable)

        if not executable_path.exists():
            raise BackendError(
                f"Executable not found: {executable}"
            )

        try:
            result = subprocess.run(
                [str(executable_path.resolve())],
                capture_output=True,
                text=True,
                check=False,
            )

        except OSError as error:
            raise BackendError(
                f"Unable to execute program: {error}"
            ) from error

        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    def build(
        self,
        source,
        cpp_file="generated/generated.cpp",
        executable="output/executable.exe",
        optimize=True,
    ):
        """
        Full pipeline:
        Python -> Bytecode -> C++ -> Native executable.
        """

        program = self.compile_source(
            source,
            optimize=optimize,
        )

        cpp_path = self.generate_cpp(cpp_file)

        compilation = self.compile_cpp(
            cpp_file=cpp_path,
            executable=executable,
        )

        return {
            "success": True,
            "program": program,
            "ir": self.ir,
            "cpp_file": cpp_path,
            "executable": compilation["executable"],
            "frontend": self.frontend_result,
            "compilation": compilation,
        }

    def save_bytecode(self, filename="generated/bytecode.bin"):
        if self.program is None:
            raise BackendError(
                "No bytecode program available"
            )

        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)

        self.program.save(str(path))

        return str(path)

    def display_ir(self):
        if self.ir is None:
            raise BackendError("No intermediate code available")

        for index, instruction in enumerate(self.ir):
            print(f"{index:04d}: {instruction}")

    def display_bytecode(self):
        if self.program is None:
            raise BackendError("No bytecode available")

        self.program.dump()


def compile_to_bytecode(source, optimize=True):
    backend = CompilerBackend()
    return backend.compile_source(source, optimize)


def compile_to_cpp(
    source,
    output_file="generated.cpp",
    optimize=True,
):
    backend = CompilerBackend()
    backend.compile_source(source, optimize)
    return backend.generate_cpp(output_file)


def build_executable(
    source,
    cpp_file="generated/generated.cpp",
    executable="output/executable.exe",
    optimize=True,
):
    backend = CompilerBackend()

    return backend.build(
        source,
        cpp_file,
        executable,
        optimize,
    )
