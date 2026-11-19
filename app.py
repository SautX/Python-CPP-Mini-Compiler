
import streamlit as st
import io
import shutil
import subprocess
import tempfile

from pathlib import Path
from contextlib import redirect_stdout

from compiler.backend import CompilerBackend
from compiler.cpp_generator import CppGenerator
from compiler.direct_cpp_generator import DirectCppGenerator
from architecture.virtual_machine import VirtualMachine


st.set_page_config(
    page_title="Python to C++ Mini Compiler",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Python to C++ Mini Compiler")
st.caption(
    "24-bit Custom Bytecode | ALU | Virtual Machine | "
    "Direct Python-to-C++ Translation"
)

DEFAULT_CODE = """a = 10.2
b = 20.3

c = a / b

print(c)
"""

if "source_code" not in st.session_state:
    st.session_state.source_code = DEFAULT_CODE


def clear_editor():
    st.session_state.source_code = DEFAULT_CODE


st.subheader("Python Source Code")

source = st.text_area(
    "Write your Python code:",
    key="source_code",
    height=250
)

col1, col2 = st.columns(2)

with col1:
    compile_button = st.button(
        "⚙️ Compile Code",
        type="primary",
        use_container_width=True
    )

with col2:
    st.button(
        "Clear Editor",
        on_click=clear_editor,
        use_container_width=True
    )


if compile_button:
    try:
        with st.spinner("Compiling Python source code..."):

            # Existing custom bytecode pipeline
            backend = CompilerBackend()
            program = backend.compile_source(source)

            # Existing bytecode-based C++ generator
            cpp_generator = CppGenerator(program)
            runtime_cpp = cpp_generator.generate()

            # New direct Python-to-C++ generator
            direct_generator = DirectCppGenerator()
            direct_cpp = direct_generator.generate(source)

            st.success("Compilation and code generation successful!")

            tab1, tab2, tab3, tab4 = st.tabs([
                "Custom Bytecode",
                "Runtime C++",
                "Direct C++",
                "Virtual Machine"
            ])

            with tab1:
                st.subheader("Custom 24-bit Bytecode")

                buffer = io.StringIO()

                with redirect_stdout(buffer):
                    dump_result = program.dump()

                bytecode_text = (
                    dump_result
                    if isinstance(dump_result, str)
                    else buffer.getvalue()
                )

                if bytecode_text.strip():
                    st.code(bytecode_text, language="text")
                else:
                    st.warning(
                        "No bytecode dump was returned. "
                        "Check compiler/bytecode.py."
                    )

            with tab2:
                st.subheader("C++ Virtual Machine Runtime")
                st.caption(
                    "C++ code containing the bytecode execution runtime."
                )

                st.code(runtime_cpp, language="cpp")

                st.download_button(
                    "Download runtime C++",
                    data=runtime_cpp,
                    file_name="generated_runtime.cpp",
                    mime="text/x-c++src"
                )

            with tab3:
                st.subheader("Direct Python-to-C++ Translation")
                st.caption(
                    "Readable C++ statements generated from supported Python."
                )

                st.code(direct_cpp, language="cpp")

                st.download_button(
                    "Download direct C++",
                    data=direct_cpp,
                    file_name="direct_generated.cpp",
                    mime="text/x-c++src"
                )

                st.divider()

                if st.button("Compile and Run Direct C++"):
                    compiler = shutil.which("g++")

                    if compiler is None:
                        st.error(
                            "GCC was not found. Check your MSYS2 UCRT64 PATH."
                        )
                    else:
                        try:
                            with tempfile.TemporaryDirectory() as temp:
                                cpp_path = Path(temp) / "direct.cpp"
                                exe_path = Path(temp) / "direct.exe"

                                cpp_path.write_text(
                                    direct_cpp,
                                    encoding="utf-8"
                                )

                                build = subprocess.run(
                                    [
                                        compiler,
                                        "-std=c++17",
                                        str(cpp_path),
                                        "-o",
                                        str(exe_path)
                                    ],
                                    capture_output=True,
                                    text=True,
                                    timeout=30
                                )

                                if build.returncode != 0:
                                    st.error("GCC compilation failed.")
                                    st.code(build.stderr, language="text")
                                else:
                                    execution = subprocess.run(
                                        [str(exe_path)],
                                        capture_output=True,
                                        text=True,
                                        timeout=10
                                    )

                                    if execution.returncode == 0:
                                        st.success(
                                            "Direct C++ compiled and executed!"
                                        )
                                        st.subheader("C++ Program Output")
                                        st.code(
                                            execution.stdout or "(No output)",
                                            language="text"
                                        )
                                    else:
                                        st.error("C++ execution failed.")
                                        st.code(
                                            execution.stderr,
                                            language="text"
                                        )

                        except subprocess.TimeoutExpired:
                            st.error("Compilation or execution timed out.")

                        except OSError as error:
                            st.error(f"System error: {error}")

            with tab4:
                st.subheader("Custom Virtual Machine Execution")

                vm = VirtualMachine(trace=False)
                result = vm.run(program)

                st.success("Virtual Machine execution completed!")

                st.write("Program output:")
                for line in result["output"]:
                    st.code(line, language="text")

                st.write("Variables:")
                st.json(result["variables"])

                st.write("Instructions executed:")
                st.write(result["steps"])

    except Exception as error:
        st.error(f"Compilation failed: {error}")


st.divider()

st.caption(
    "Educational Python-to-C++ Compiler | "
    "Custom 24-bit Instruction Set | Python | C++ | GCC"
)
