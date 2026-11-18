import re
from dataclasses import dataclass


@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int


TOKEN_SPEC = [
    ("NUMBER",   r"\d+"),
    ("IDENTIFIER", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("PLUS",     r"\+"),
    ("MINUS",    r"-"),
    ("MULTIPLY", r"\*"),
    ("DIVIDE",   r"/"),
    ("MODULO",   r"%"),
    ("ASSIGN",   r"="),
    ("LPAREN",   r"\("),
    ("RPAREN",   r"\)"),
    ("COMMA",    r","),
    ("NEWLINE",  r"\n"),
    ("SKIP",     r"[ \t]+"),
    ("COMMENT",  r"\#[^\n]*"),
    ("MISMATCH", r"."),
]

MASTER_REGEX = re.compile(
    "|".join(
        f"(?P<{name}>{pattern})"
        for name, pattern in TOKEN_SPEC
    )
)


def tokenize(source):

    tokens = []

    line = 1
    line_start = 0

    for match in MASTER_REGEX.finditer(source):

        kind = match.lastgroup
        value = match.group()
        column = match.start() - line_start + 1

        if kind == "NUMBER":
            tokens.append(
                Token("NUMBER", value, line, column)
            )

        elif kind == "IDENTIFIER":

            token_type = (
                "PRINT" if value == "print"
                else "IDENTIFIER"
            )

            tokens.append(
                Token(token_type, value, line, column)
            )

        elif kind == "NEWLINE":

            tokens.append(
                Token("NEWLINE", value, line, column)
            )

            line += 1
            line_start = match.end()

        elif kind in (
            "SKIP",
            "COMMENT"
        ):
            continue

        elif kind == "MISMATCH":

            raise SyntaxError(
                f"Unexpected character {value!r} "
                f"at line {line}, column {column}"
            )

        else:

            tokens.append(
                Token(kind, value, line, column)
            )

    tokens.append(
        Token("EOF", "", line, len(source) - line_start + 1)
    )

    return tokens