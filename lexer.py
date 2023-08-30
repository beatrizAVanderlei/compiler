import re
from typing import Any


class Token:
    def __init__(self, token_type, value, line):
        self.token_type = token_type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.token_type}, '{self.value}')"


class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.current_line = 0
        self.tokens: list[Token] = []
        self.symbol_table: dict[Token, dict[str, Any]] = {}
        # the order of the patterns matters
        self.patterns: list[tuple[str, str]] = [
            # reserved tokens
            (r"\bif\b", "IF"),
            (r"\belse\b", "ELSE"),
            (r"\bwhile\b", "WHILE"),
            (r"\bint\b", "INT"),
            (r"\bbool\b", "BOOL"),
            (r"\btrue\b", "TRUE"),
            (r"\bfalse\b", "FALSE"),
            (r"\bnot\b", "NOT"),
            (r"\band\b", "AND"),
            (r"\bor\b", "OR"),
            (r"\bprint\b", "PRINT"),
            (r"\breturn\b", "RETURN"),
            (r"\bfunction\b", "FUNCTION"),
            (r"\bprocedure\b", "PROCEDURE"),
            (r"\bbreak\b", "BREAK"),
            (r"\bcontinue\b", "CONTINUE"),
            # symbols
            (r"->", "ARROW"),
            (r"==", "EQUAL"),
            (r"!=", "DIFFERENT"),
            (r">=", "GREATER_OR_EQUAL"),
            (r"<=", "LESS_OR_EQUAL"),
            (r"\+", "PLUS"),
            (r"-", "MINUS"),
            (r"\*", "MULTIPLY"),
            (r"/", "DIVIDE"),
            (r"\%", "MODULE"),
            (r"=", "ASSIGN"),
            (r";", "SEMICOLON"),
            (r",", "COLON"),
            (r"\(", "LPAREN"),
            (r"\)", "RPAREN"),
            (r">", "GREATER"),
            (r"<", "LESS"),
            (r"\{", "LBRACE"),
            (r"\}", "RBRACE"),
            # others
            (r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", "IDENTIFIER"),
            (r"\b[0-9]+\b", "INTEGER"),
        ]

    def lex(self):
        self.code = self.code.split("\n")

        for line in self.code:
            self.current_line += 1
            line = line.strip()

            while line:
                matched = False
                for pattern, token_type in self.patterns:
                    match = re.match(pattern, line)
                    if match:
                        matched = True
                        value = match.group(0)
                        token = Token(
                            token_type=token_type, value=value, line=self.current_line
                        )
                        self.tokens.append(token)

                        if token_type == "IDENTIFIER":
                            self.symbol_table[token] = {
                                "variable_type": None,
                                "variable_value": None,
                                "scope": None,
                                "line": self.current_line,
                            }

                        line = line[len(value) :].strip()
                        break

                if not matched:
                    raise ValueError(f"Invalid syntax in line {self.current_line}")
