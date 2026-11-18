import ast
import dis


def show_cpython_disassembly(source):

    try:

        python_ast = ast.parse(source)

        compiled_code = compile(
            python_ast,
            "<source>",
            "exec"
        )

        print("\n================================")
        print("       CPYTHON BYTECODE")
        print("================================")

        dis.dis(compiled_code)

    except SyntaxError as error:

        print("CPython syntax error:")
        print(error)


def get_cpython_instructions(source):

    python_ast = ast.parse(source)

    compiled_code = compile(
        python_ast,
        "<source>",
        "exec"
    )

    return list(
        dis.get_instructions(compiled_code)
    )