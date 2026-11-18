# Python-to-C++ Mini Compiler

A simple educational compiler that translates a supported subset
of Python-like source code into custom 24-bit bytecode and then
generates C++17 code.

## Project Overview

This project demonstrates the fundamental stages of compiler design:

Python Source Code
|
v
Lexical Analysis
|
v
Syntax Analysis
|
v
Abstract Syntax Tree
|
v
Intermediate Representation
|
v
Custom 24-bit Bytecode
|
v
Bytecode Optimization
|
v
C++ Code Generation
|
v
GCC Compilation
|
v
Executable Program

## Features

- Python-like source code input
- Lexer and parser
- Abstract syntax tree generation
- Intermediate representation
- Custom 24-bit instruction format
- Bytecode decoder
- Basic constant folding
- C++17 code generation
- GCC integration
- Arithmetic Logic Unit simulation
- Virtual processor architecture
- Register and memory simulation
- PySide6 graphical interface

## Instruction Format

Each custom instruction is 24 bits:

| Field   |    Size |
| ------- | ------: |
| Opcode  |  8 bits |
| Operand | 16 bits |
| Total   | 24 bits |

Instruction layout:

[ OPCODE: 8 BITS ][ OPERAND: 16 BITS ]

## Supported Operations

- Addition (+)
- Subtraction (-)
- Multiplication (\*)
- Integer division (/ in current C++ backend)
- Modulus (%)
- Variable assignment
- Integer constants
- Parentheses
- Unary minus
- print() for integer expressions

## Technologies

- Python
- C++
- PySide6
- GCC / MinGW-w64
- VS Code

## Requirements

- Python 3.10 or newer
- GCC compiler
- PySide6

## Installation

Clone or download the project.

Install dependencies:

    pip install -r requirements.txt

Ensure GCC is installed and available in PATH.

## Run the CLI Compiler

    python main.py examples/sample.py

## Run the GUI

    python -m gui.app

## Run Tests

    python -m unittest discover -s tests -v

## Generated Files

The compiler generates:

    generated/bytecode.bin
    generated/intermediate_code.txt
    generated/generated.cpp

The executable is saved to:

    output/executable.exe

## Project Structure

    Python_CPP_Mini_Compiler/
    |
    |-- compiler/
    |-- architecture/
    |-- examples/
    |-- generated/
    |-- output/
    |-- gui/
    |-- tests/
    |
    |-- main.py
    |-- requirements.txt
    |-- README.md
    |-- .gitignore

## Educational Purpose

This project is designed to demonstrate compiler construction,
instruction encoding, code generation, and virtual processor
simulation.

It is not a complete implementation of the Python language.

## Future Improvements

- Python string support
- Conditional statements
- Loops
- Function support
- Improved bytecode optimization
- Live register visualization
- Step-by-step virtual processor execution
- Syntax highlighting
- Debugging tools
