from pathlib import Path

from .backend import generate_cpp


class CPPGenerator:

    def __init__(self, output_directory="generated"):

        self.output_directory = Path(
            output_directory
        )

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True
        )

    def generate(self, program):

        return generate_cpp(program)

    def save(self, program, filename="generated.cpp"):

        cpp_code = self.generate(program)

        output_file = (
            self.output_directory / filename
        )

        output_file.write_text(
            cpp_code,
            encoding="utf-8"
        )

        return output_file